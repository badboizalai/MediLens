"""Authorization matrix tests (SEC-AZ-01/02, BR-006, BR-030).

Parametrise over every operation that takes a resource ID. Uses synthetic factories only.
"""
import pytest

OPERATIONS = [
    ("GET", "/api/v1/medical-documents/{id}"),
    ("GET", "/api/v1/extractions/{id}"),
    ("POST", "/api/v1/extractions/{id}/confirm"),
    ("GET", "/api/v1/findings?documentId={id}"),
]

CASES = [
    # actor,            expected
    ("owner",           {200, 202, 204, 422, 412}),   # allowed (may still fail business validation)
    ("stranger",        {404}),
    ("expired_share",   {404}),
    ("admin_no_glass",  {404, 403}),
    ("anonymous",       {401}),
]


@pytest.mark.parametrize("method,path", OPERATIONS)
@pytest.mark.parametrize("actor,expected", CASES)
async def test_sec_az_02_matrix(method, path, actor, expected, client, world):
    """world fixture creates: owner with a document, a stranger, an expired share, an admin."""
    doc = world.owner_document
    headers = world.auth_headers(actor)
    headers.update({"If-Match": doc.etag, "Idempotency-Key": world.new_key()})
    resp = await client.request(method, path.format(id=doc.id), headers=headers)
    assert resp.status_code in expected, (actor, method, path, resp.status_code, resp.text)
    if actor in {"stranger", "expired_share"}:
        assert await world.audit_contains("access_denied", resource_id=doc.id)
