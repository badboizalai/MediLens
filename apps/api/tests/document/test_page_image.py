from uuid import UUID, uuid4

import pytest
from botocore.exceptions import ClientError
from fastapi.testclient import TestClient
from medilens.modules.document.api import router as doc_router
from medilens.modules.document.infra.s3_storage import S3PageImages, StorageSettings

from .conftest import Env
from .test_upload import request


class FakePages:
    def __init__(self) -> None:
        self.pages = {1, 2}
        self.ttl: int | None = None

    def presign_page(self, document_id: UUID, page_no: int, expires_in: int) -> str | None:
        self.ttl = expires_in
        if page_no not in self.pages:
            return None
        return f"https://pages.test/pre/{document_id}/{page_no:04d}.png?sig=x"


@pytest.fixture
def pages(env: Env) -> FakePages:
    fake = FakePages()
    env.client.app.dependency_overrides[doc_router.get_page_images] = lambda: fake  # type: ignore[attr-defined]
    return fake


def test_owner_gets_short_lived_url(env: Env, pages: FakePages) -> None:
    doc_id = request(env).json()["document_id"]
    r = env.client.get(f"/v1/documents/{doc_id}/pages/2/image")
    assert r.status_code == 200
    assert r.json() == {
        "url": f"https://pages.test/pre/{doc_id}/0002.png?sig=x",
        "expiresIn": doc_router.PAGE_URL_TTL_SECONDS,
    }
    assert pages.ttl == 300 and r.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("page", [0, -1, 3])
def test_page_out_of_range_is_404(env: Env, pages: FakePages, page: int) -> None:
    doc_id = request(env).json()["document_id"]
    assert env.client.get(f"/v1/documents/{doc_id}/pages/{page}/image").status_code == 404


def test_other_user_and_unknown_document_are_404(env: Env, pages: FakePages) -> None:
    doc_id = request(env).json()["document_id"]
    env.as_user("bob")
    assert env.client.get(f"/v1/documents/{doc_id}/pages/1/image").status_code == 404
    assert env.client.get(f"/v1/documents/{uuid4()}/pages/1/image").status_code == 404


def test_unauthenticated_is_401() -> None:
    from medilens.main import create_app

    r = TestClient(create_app()).get(f"/v1/documents/{uuid4()}/pages/1/image")
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")


class FakeS3:
    def __init__(self, keys: set[str]) -> None:
        self.keys = keys

    def head_object(self, Bucket: str, Key: str) -> None:  # noqa: N803
        if Key not in self.keys:
            raise ClientError({"Error": {"Code": "404"}}, "HeadObject")

    def generate_presigned_url(self, op: str, Params: dict, ExpiresIn: int) -> str:  # noqa: N803
        return f"https://s3.test/{Params['Bucket']}/{Params['Key']}?op={op}&exp={ExpiresIn}"


def test_s3_adapter_presigns_only_existing_pages() -> None:
    doc = uuid4()
    s = StorageSettings(pages_bucket="pages-test")
    imgs = S3PageImages(s, FakeS3({f"pre/{doc}/0001.png"}))
    assert imgs.presign_page(doc, 1, 300) == (
        f"https://s3.test/pages-test/pre/{doc}/0001.png?op=get_object&exp=300"
    )
    assert imgs.presign_page(doc, 2, 300) is None
