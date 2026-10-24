"""boto3 S3 adapter. Works with AWS S3 and local SeaweedFS/MinIO via an endpoint URL."""

import hashlib
from functools import lru_cache
from typing import Any
from uuid import UUID

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings, SettingsConfigDict

from medilens.modules.document.domain.models import Presigned, quarantine_key

_CHUNK = 1024 * 1024


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MEDILENS_S3_", extra="ignore")

    bucket: str = "medilens-quarantine"
    endpoint_url: str | None = None  # set for SeaweedFS/MinIO
    region: str = "ap-southeast-1"
    pages_bucket: str = "medilens-phi"  # worker pages bucket (WORKER_PAGES_BUCKET), SSE-KMS


@lru_cache
def get_storage_settings() -> StorageSettings:
    return StorageSettings()


class S3Storage:
    def __init__(self, settings: StorageSettings, client: Any | None = None) -> None:
        self._bucket = settings.bucket
        self._client = client or boto3.client(
            "s3",
            endpoint_url=settings.endpoint_url,
            region_name=settings.region,
            config=Config(signature_version="s3v4"),
        )

    def presign_put(
        self, key: str, content_type: str, size_bytes: int, expires_in: int
    ) -> Presigned:
        # A presigned PUT cannot carry a content-length-range policy (that is POST-only), so
        # Content-Type and the exact Content-Length are signed headers: S3 rejects any other
        # type or size. complete() re-checks the stored size anyway.
        url = self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket,
                "Key": key,
                "ContentType": content_type,
                "ContentLength": size_bytes,
            },
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
        return Presigned(url, {"Content-Type": content_type}, expires_in)

    def size(self, key: str) -> int | None:
        try:
            head = self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise
        return int(head["ContentLength"])

    def read_head(self, key: str, n: int) -> bytes:
        obj = self._client.get_object(Bucket=self._bucket, Key=key, Range=f"bytes=0-{n - 1}")
        data: bytes = obj["Body"].read()
        return data

    def sha256(self, key: str) -> str:
        body = self._client.get_object(Bucket=self._bucket, Key=key)["Body"]
        h = hashlib.sha256()
        for chunk in body.iter_chunks(_CHUNK):
            h.update(chunk)
        return h.hexdigest()

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)


class S3PageImages:
    """Processed page PNGs written by the worker at `pre/<document_id>/<page:04d>.png`."""

    def __init__(self, settings: StorageSettings, client: Any | None = None) -> None:
        self._bucket = settings.pages_bucket
        self._client = client or boto3.client(
            "s3",
            endpoint_url=settings.endpoint_url,
            region_name=settings.region,
            config=Config(signature_version="s3v4"),
        )

    def presign_page(self, document_id: UUID, page_no: int, expires_in: int) -> str | None:
        key = f"pre/{document_id}/{page_no:04d}.png"
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise
        url: str = self._client.generate_presigned_url(
            "get_object", Params={"Bucket": self._bucket, "Key": key}, ExpiresIn=expires_in
        )
        return url


class S3DsrStorage:
    """Export and erase across the quarantine bucket and the worker pages bucket."""

    def __init__(self, settings: StorageSettings, client: Any | None = None) -> None:
        self._buckets = (settings.bucket, settings.pages_bucket)
        self._client = client or boto3.client(
            "s3",
            endpoint_url=settings.endpoint_url,
            region_name=settings.region,
            config=Config(signature_version="s3v4"),
        )

    def _keys(self, bucket: str, prefix: str) -> list[str]:
        pages = self._client.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix)
        return [o["Key"] for p in pages for o in p.get("Contents", [])]

    def presign_original(self, profile_id: UUID, document_id: UUID, expires_in: int) -> str | None:
        # raw/ is the worker's durable copy; quarantine/ exists until the worker has copied it
        for bucket, prefix in (
            (self._buckets[1], f"raw/{document_id}/"),
            (self._buckets[0], quarantine_key(profile_id, document_id)),
        ):
            keys = self._keys(bucket, prefix)
            if keys:
                url: str = self._client.generate_presigned_url(
                    "get_object", Params={"Bucket": bucket, "Key": keys[0]}, ExpiresIn=expires_in
                )
                return url
        return None

    def list_prefix(self, prefix: str) -> list[str]:
        return [k for b in self._buckets for k in self._keys(b, prefix)]

    def delete_prefix(self, prefix: str) -> None:
        for b in self._buckets:
            keys = self._keys(b, prefix)
            for i in range(0, len(keys), 1000):  # DeleteObjects limit
                self._client.delete_objects(
                    Bucket=b, Delete={"Objects": [{"Key": k} for k in keys[i : i + 1000]]}
                )
