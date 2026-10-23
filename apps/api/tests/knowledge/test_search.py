from medilens.core.db import scope_to_profiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from .conftest import ARTICLES, Env


def ka(n: str) -> str:
    return (ARTICLES / f"KA-{n}.md").read_text("utf-8")


def test_cross_user_query_returns_zero_results(env: Env) -> None:
    env.index(env.bob, "bob private marker zebra", "bob-1")
    assert env.search(env.alice, "bob private marker zebra") == []
    # Alice may not even address Bob's profile: 404, nothing leaks.
    r = env.client.post(f"/v1/profiles/{env.bob}/knowledge/search", json={"query": "zebra"})
    assert r.status_code == 404


def test_owner_gets_own_profile_chunks_and_articles(env: Env) -> None:
    env.ingest(ka("001"))
    env.index(env.alice, "my synthetic liver note", "alice-1")
    got = env.search(env.alice, "FDI tooth numbers quadrant")
    assert got[0]["scope"] == "article" and got[0]["article_id"] == "KA-001"
    assert got[0]["citations"][0]["url"].startswith("https://")
    mine = env.search(env.alice, "synthetic liver note", k=1)
    assert mine[0]["scope"] == "profile"


def test_rls_alone_hides_foreign_chunks(env: Env) -> None:
    """Without the code filter: app_rw scoped to Alice still sees no Bob rows, cannot write them."""
    env.index(env.bob, "bob secret", "bob-1")
    with Session(env.engine) as s, s.begin():
        s.execute(text("SET LOCAL ROLE app_rw"))
        scope_to_profiles(s, [env.alice])
        assert s.execute(text("SELECT count(*) FROM clinical.knowledge_chunks")).scalar_one() == 0


def test_app_role_cannot_delete_public_chunks(env: Env) -> None:
    env.ingest(ka("001"))
    before = env.count()
    with Session(env.engine) as s, s.begin():
        s.execute(text("SET LOCAL ROLE app_rw"))
        scope_to_profiles(s, [env.alice])
        s.execute(text("DELETE FROM clinical.knowledge_chunks"))
    assert env.count() == before


def test_drafts_excluded_unless_allowed(env: Env) -> None:
    env.ingest(ka("001"))
    env.drafts["allow"] = False
    assert env.search(env.alice, "FDI tooth") == []
    env.ingest(ka("001").replace("cso_review_date: null", "cso_review_date: 2026-11-01"))
    assert env.search(env.alice, "FDI tooth")[0]["article_id"] == "KA-001"


def test_reingest_is_idempotent_and_reindex_replaces(env: Env) -> None:
    env.ingest(ka("001"))
    env.ingest(ka("001"))
    first = env.count()
    env.index(env.alice, "one", "r")
    env.index(env.alice, "two", "r")
    assert env.count() == first + 1


def test_authz(env: Env) -> None:
    url = f"/v1/profiles/{env.alice}/knowledge/search"
    assert env.anon.post(url, json={"query": "x"}).status_code == 401
    env.current["sub"] = "bob"
    assert env.client.post(url, json={"query": "x"}).status_code == 404
    env.current["sub"] = "nobody"
    assert env.client.post(url, json={"query": "x"}).status_code == 404


def test_validation(env: Env) -> None:
    url = f"/v1/profiles/{env.alice}/knowledge/search"
    assert env.client.post(url, json={"query": "x", "k": 11}).status_code == 400
    assert env.client.post(url, json={"query": ""}).status_code == 400
