import json
import time
import uuid
from pathlib import Path

import boto3
import pytest
from jsonschema import Draft202012Validator
from medilens_worker.extraction import deps
from medilens_worker.extraction.service import PIPELINE_VERSION, ExtractionRun
from medilens_worker.jobs.registry import REGISTRY, JobContext
from medilens_worker.main import build_extract_deps
from medilens_worker.queue.events import InMemoryEventSink
from medilens_worker.storage.results import S3ResultStore, to_object
from moto import mock_aws

CONTRACTS = Path(__file__).resolve().parents[4] / "docs/architecture/contracts"
RESULT = Draft202012Validator(json.loads((CONTRACTS / "extraction-result.schema.json").read_text()))
COMPLETED = Draft202012Validator(
    json.loads((CONTRACTS / "extraction-completed.schema.json").read_text())
)
DOC = str(uuid.uuid4())


def make_run(doc=DOC):
    return ExtractionRun(doc, "dental", "m", "extract-v1", 0.01, 0.9, {"teeth": []}, [])


def test_object_matches_contract_schema():
    run = make_run()
    assert uuid.UUID(run.run_id) and run.pipeline_version == PIPELINE_VERSION
    RESULT.validate(to_object(run))


@pytest.fixture
def s3_store():
    with mock_aws():
        boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="res")
        yield S3ResultStore("res")


def test_s3_roundtrip_key_sse_and_latest(s3_store):
    first = make_run()
    s3_store.save(first)
    time.sleep(1.1)  # uuid7 is ms-ordered
    second = make_run()
    s3_store.save(second)
    c = boto3.client("s3")
    key = f"extractions/{DOC}/{second.run_id}.json"
    assert c.head_object(Bucket="res", Key=key)["ServerSideEncryption"] == "aws:kms"
    RESULT.validate(json.loads(c.get_object(Bucket="res", Key=key)["Body"].read()))
    assert s3_store.latest(DOC) == second
    assert s3_store.latest(str(uuid.uuid4())) is None


def test_finalize_emits_completed_event_idempotently():
    sink = InMemoryEventSink()
    d = build_extract_deps({"ENV": "local"}, events=sink)
    run = make_run()
    d.save_run(run)
    deps.configure(d)
    try:
        ctx = JobContext(DOC, 1, lambda s: None)
        REGISTRY["document.finalize"].handler(ctx)
        REGISTRY["document.finalize"].handler(ctx)
    finally:
        deps.configure(None)
    assert len(sink.events) == 2 and sink.events[0] == sink.events[1]
    COMPLETED.validate(sink.events[0])
    assert sink.events[0]["runId"] == run.run_id


def test_results_bucket_required_outside_local():
    base = {"AI_GATEWAY_URL": "u", "AI_GATEWAY_SERVICE_SECRET": "s", "WORKER_TENANT_ID": "t"}
    with pytest.raises(RuntimeError, match="EXTRACTION_RESULTS_BUCKET"):
        build_extract_deps(base)


def test_latest_picks_greatest_run_id_not_last_modified(s3_store):
    older, newer = sorted([make_run(), make_run()], key=lambda r: r.run_id)
    s3_store.save(newer)  # written first, so `older` has the later LastModified
    time.sleep(1.1)
    s3_store.save(older)
    assert s3_store.latest(DOC) == newer
