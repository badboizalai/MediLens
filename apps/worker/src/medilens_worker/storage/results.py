"""Extraction result store (ADR-0005 decision 3). Objects are PHI: never log them."""

import json

import boto3

from medilens_worker.extraction.service import ExtractionRun
from medilens_worker.storage.s3 import sse_kms


def to_object(r: ExtractionRun) -> dict:
    """Shape of docs/architecture/contracts/extraction-result.schema.json."""
    return {
        "schemaVersion": 1,
        "documentId": r.document_id,
        "runId": r.run_id,
        "unit": r.unit,
        "model": r.model,
        "promptVersion": r.prompt_version,
        "pipelineVersion": r.pipeline_version,
        "costUsd": r.cost_usd,
        "confidence": r.confidence,
        "repaired": r.repaired,
        "flags": r.flags,
        "result": r.result,
    }


def from_object(o: dict) -> ExtractionRun:
    return ExtractionRun(
        document_id=o["documentId"],
        unit=o["unit"],
        model=o["model"],
        prompt_version=o["promptVersion"],
        cost_usd=o["costUsd"],
        confidence=o["confidence"],
        result=o["result"],
        flags=o["flags"],
        repaired=o["repaired"],
        run_id=o["runId"],
        pipeline_version=o.get("pipelineVersion", ""),
    )


class InMemoryResultStore:
    def __init__(self) -> None:
        self._runs: dict[str, ExtractionRun] = {}

    def save(self, run: ExtractionRun) -> None:
        self._runs[run.document_id] = run

    def latest(self, document_id: str) -> ExtractionRun | None:
        return self._runs.get(document_id)


class S3ResultStore:
    def __init__(
        self, bucket: str, endpoint_url: str | None = None, kms_key_id: str | None = None
    ) -> None:
        self._c = boto3.client("s3", endpoint_url=endpoint_url)
        self._b, self._sse = bucket, sse_kms(kms_key_id)

    def save(self, run: ExtractionRun) -> None:
        self._c.put_object(
            Bucket=self._b,
            Key=f"extractions/{run.document_id}/{run.run_id}.json",
            Body=json.dumps(to_object(run)).encode(),
            **self._sse,  # ADR-0005: SSE-KMS
        )

    def latest(self, document_id: str) -> ExtractionRun | None:
        objs: list[dict] = []
        for pg in self._c.get_paginator("list_objects_v2").paginate(
            Bucket=self._b, Prefix=f"extractions/{document_id}/"
        ):
            objs += pg.get("Contents", [])
        if not objs:
            return None
        # runId is uuid7 (time-ordered); LastModified has 1 s resolution and can disagree
        newest = max(objs, key=lambda o: o["Key"].rsplit("/", 1)[-1])
        body = self._c.get_object(Bucket=self._b, Key=newest["Key"])["Body"].read()
        return from_object(json.loads(body))
