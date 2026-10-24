"""Ingest of the worker's extraction result (ADR-0005/0006). Result objects are PHI: never log them.

The S3 object is read through an injectable port; rows are written only by the definer function
clinical.ingest_extraction, which derives profile_id from the document row.
"""

import json
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class ResultReader(Protocol):
    def read(self, key: str) -> bytes: ...


class S3ResultReader:
    def __init__(self, bucket: str, client: Any) -> None:
        self._bucket, self._client = bucket, client

    def read(self, key: str) -> bytes:
        return self._client.get_object(Bucket=self._bucket, Key=key)["Body"].read()


def result_key(document_id: UUID, run_id: UUID) -> str:
    return f"extractions/{document_id}/{run_id}.json"


def flatten(result: Any) -> list[dict[str, Any]]:
    """One row per cited leaf ({value, confidence, source}); same walk as the worker's check."""
    rows: list[dict[str, Any]] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, list):
            for i, x in enumerate(node):
                walk(x, f"{path}[{i}]")
        elif isinstance(node, dict):
            src = node.get("source")
            if isinstance(src, dict) and "confidence" in node:
                v = node.get("value")
                rows.append(
                    {
                        "field_path": path,
                        "value": None if v is None else str(v),
                        "confidence": node["confidence"],
                        "source_page": src.get("page"),
                        "source_box": src.get("bbox"),
                    }
                )
                return
            for k, x in node.items():
                walk(x, f"{path}.{k}" if path else k)

    walk(result, "")
    return rows


def ingest(session: Session, doc: dict[str, Any]) -> str:
    """doc: a validated extraction-result object. Returns unknown | duplicate | ingested."""
    return session.execute(
        text(
            "SELECT clinical.ingest_extraction(CAST(:doc AS uuid), CAST(:run AS uuid), :pv, :model, :prompt, "
            "CAST(:conf AS real), CAST(:cost AS numeric), "
            "CAST(:raw AS jsonb), CAST(:fields AS jsonb))"
        ),
        {
            "doc": doc["documentId"],
            "run": doc["runId"],
            "pv": doc.get("pipelineVersion") or None,
            "model": doc["model"],
            "prompt": doc["promptVersion"],
            "conf": doc["confidence"],
            "cost": doc["costUsd"],
            "raw": json.dumps(doc["result"]),
            "fields": json.dumps(flatten(doc["result"])),
        },
    ).scalar_one()
