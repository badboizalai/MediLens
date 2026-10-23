"""S3 page store. Keys are `<kind>/<document_id>/...` (opaque ids only, no PHI in keys)."""

import json
from dataclasses import asdict

import boto3

from medilens_worker.ocr.types import Metrics, OcrBox, OcrPage, PreprocessedPage, RetakeReason


class S3PageStore:
    def __init__(
        self, bucket: str, raw_bucket: str | None = None, endpoint_url: str | None = None
    ) -> None:
        self._c = boto3.client("s3", endpoint_url=endpoint_url)
        self._b, self._raw_b = bucket, raw_bucket or bucket

    def _keys(self, bucket: str, prefix: str) -> list[str]:
        out: list[str] = []
        for pg in self._c.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
            out += [o["Key"] for o in pg.get("Contents", [])]
        return sorted(out)  # page numbers are zero-padded

    def _get(self, bucket: str, key: str) -> bytes:
        return self._c.get_object(Bucket=bucket, Key=key)["Body"].read()

    def _put(self, key: str, body: bytes) -> None:
        self._c.put_object(Bucket=self._b, Key=key, Body=body, ServerSideEncryption="AES256")

    def raw_pages(self, document_id: str) -> list[bytes]:
        return [self._get(self._raw_b, k) for k in self._keys(self._raw_b, f"raw/{document_id}/")]

    def save_preprocessed(self, document_id: str, pages: list[PreprocessedPage]) -> None:
        for p in pages:
            base = f"pre/{document_id}/{p.page:04d}"
            self._put(f"{base}.png", p.image)
            meta = {"quality": p.quality, "metrics": asdict(p.metrics)}
            self._put(f"{base}.json", json.dumps(meta).encode())

    def preprocessed(self, document_id: str) -> list[PreprocessedPage]:
        out = []
        for k in self._keys(self._b, f"pre/{document_id}/"):
            if k.endswith(".png"):
                meta = json.loads(self._get(self._b, k[:-4] + ".json"))
                m = Metrics(**meta["metrics"])
                out.append(
                    PreprocessedPage(int(k[-8:-4]), self._get(self._b, k), meta["quality"], m)
                )
        return out

    def save_ocr(self, document_id: str, pages: list[OcrPage]) -> None:
        for p in pages:
            self._put(f"ocr/{document_id}/{p.page:04d}.json", json.dumps(asdict(p)).encode())

    def ocr_pages(self, document_id: str) -> list[OcrPage]:
        out = []
        for k in self._keys(self._b, f"ocr/{document_id}/"):
            d = json.loads(self._get(self._b, k))
            d["boxes"] = [OcrBox(**b) for b in d["boxes"]]
            out.append(OcrPage(**d))
        return out

    def save_retake(self, document_id: str, page: int, reason: RetakeReason) -> None:
        body = json.dumps({"page": page, "reason": reason.value}).encode()
        self._put(f"retake/{document_id}.json", body)
