"""D107 / SEC-AZ-01..05: route-level authorisation matrix over the real `create_app()`.

Every route the app exposes must be classified below (a new unclassified route fails
`test_every_route_is_classified`). The matrix then calls each route as six actors and compares the
status with the expectation of its class. Set AUTHZ_MATRIX_OUT=<file.md> to regenerate the table
in docs/qa/authz-matrix.md from the observed statuses. Synthetic data only.
"""

import os
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from medilens.core.db import make_engine, make_session_factory
from medilens.main import create_app
from medilens.modules.admin.api import router as admin_r
from medilens.modules.clinical.api import router as clinical_r
from medilens.modules.document.api import router as doc_r
from medilens.modules.document.application.rate_limit import InMemoryLimiter
from medilens.modules.identity.api import router as identity_r
from medilens.modules.knowledge.api import router as knowledge_r
from medilens.modules.sharing.api import router as sharing_r
from medilens.shared.auth import Principal, get_current_user, get_token_validator
from sqlalchemy import event, text

from tests.db.conftest import API_DIR, pg_url  # noqa: F401

Route = tuple[str, str]  # (METHOD, path template)

# Why each unauthenticated route is allowed to be public (SEC-AZ-01). Nothing else may be.
PUBLIC: dict[Route, str] = {
    ("GET", "/healthz"): "liveness probe, no data",
    ("GET", "/readyz"): "readiness probe, no data",
    ("GET", "/openapi.json"): "API schema; hidden in prod (docs_enabled=False)",
    ("GET", "/docs"): "Swagger UI; hidden in prod (docs_enabled=False)",
    ("GET", "/docs/oauth2-redirect"): "Swagger UI helper; hidden in prod",
}

# Access classes: who may use a route. Everything else must be denied.
SELF = "self"  # any authenticated user, acts on their own account only
OWNER = "owner"  # the profile owner only (RLS + ownership check)
GRANTEE = "grantee"  # the grantee of an active share only
ADMIN = "admin"  # role medilens-admin, no PHI
GLASS = "break-glass"  # admin with an open break-glass grant

ROUTES: dict[Route, str] = {
    ("GET", "/v1/me"): SELF,
    ("DELETE", "/v1/me"): SELF,
    ("GET", "/v1/me/export"): SELF,
    ("POST", "/v1/me/consents/{consent_type}/withdraw"): SELF,
    ("POST", "/v1/profiles/{profile_id}/documents"): OWNER,
    ("POST", "/v1/documents/{document_id}/complete"): OWNER,
    ("GET", "/v1/documents/{document_id}"): OWNER,
    ("GET", "/v1/documents/{document_id}/pages/{page_no}/image"): OWNER,
    ("GET", "/v1/documents/{document_id}/events"): OWNER,
    ("GET", "/v1/documents/{document_id}/fields"): OWNER,
    ("PATCH", "/v1/documents/{document_id}/fields/{field_id}"): OWNER,
    ("POST", "/v1/documents/{document_id}/confirm"): OWNER,
    ("GET", "/v1/profiles/{profile_id}/findings"): OWNER,
    ("POST", "/v1/profiles/{profile_id}/reported-findings"): OWNER,
    ("POST", "/v1/profiles/{profile_id}/knowledge/search"): OWNER,
    ("POST", "/v1/profiles/{profile_id}/shares"): OWNER,
    ("GET", "/v1/profiles/{profile_id}/shares"): OWNER,
    ("DELETE", "/v1/shares/{share_id}"): OWNER,
    ("GET", "/v1/shared/{share_id}"): GRANTEE,
    ("GET", "/v1/shared/{share_id}/findings"): GRANTEE,
    ("GET", "/v1/admin/stats"): ADMIN,
    ("POST", "/v1/admin/break-glass"): ADMIN,
    ("GET", "/v1/admin/break-glass/{grant_id}/documents"): GLASS,
}

ACTORS = ("anonymous", "other", "grantee", "admin", "owner", "admin+break-glass")
# Order matters: the owner runs late because DELETE /shares revokes the grantee's share.
RUN_ORDER = ("anonymous", "other", "grantee", "admin", "admin+break-glass", "owner")
DENIED = {403, 404}


def expected(cls: str, actor: str) -> str:
    """'401' | 'deny' (403/404) | '403' | 'allow' (authorised, any non-auth outcome)."""
    if actor == "anonymous":
        return "401"
    if cls == SELF:
        return "allow"
    if cls == OWNER:
        return "allow" if actor == "owner" else "deny"
    if cls == GRANTEE:
        return "allow" if actor == "grantee" else "deny"
    if cls == ADMIN:
        return "allow" if actor.startswith("admin") else "403"
    return "allow" if actor == "admin+break-glass" else "403"  # GLASS


def matches(exp: str, status: int) -> bool:
    if exp == "401":
        return status == 401
    if exp == "403":
        return status == 403
    if exp == "deny":
        return status in DENIED
    return status not in {401, 403, 404} and status < 500


def enumerate_routes(app: FastAPI) -> set[Route]:
    """Methods x paths from the OpenAPI schema plus top-level routes hidden from it (docs)."""
    found = {
        (m.upper(), p) for p, ops in app.openapi()["paths"].items() for m in ops if m != "head"
    }
    for r in app.routes:
        path, methods = getattr(r, "path", None), getattr(r, "methods", None)
        if path and methods:
            found |= {(m, path) for m in methods if m != "HEAD"}
    return found


def test_every_route_is_classified() -> None:
    """(c) A new route without a classification fails here; a stale entry fails too."""
    classified = set(PUBLIC) | set(ROUTES)
    live = enumerate_routes(create_app())
    unclassified, stale = live - classified, classified - live
    assert not unclassified, f"unclassified routes (add to PUBLIC or ROUTES): {unclassified}"
    assert not stale, f"classification for routes that no longer exist: {stale}"
    assert not set(PUBLIC) & set(ROUTES)
    assert all(reason for reason in PUBLIC.values())


@dataclass
class World:
    clients: dict[str, TestClient]
    current: dict[str, Principal]
    ids: dict[str, str]
    grant_id: str


SUBS = ("alice", "bob", "carol", "root-admin")  # owner, other user, grantee, admin
ADMIN_P = Principal(sub="root-admin", roles=frozenset({"medilens-admin"}))


class _Pages:
    def presign_page(self, document_id: UUID, page_no: int, expires_in: int) -> str | None:
        return f"https://pages.test/{document_id}/{page_no}"


class _Storage:
    """Enough of ObjectStorage/DsrStorage for authz probing; nothing is ever stored."""

    def presign_put(self, key, content_type, size_bytes, expires_in):  # type: ignore[no-untyped-def]
        from medilens.modules.document.domain.models import Presigned

        return Presigned(f"https://storage.test/{key}", {}, expires_in)

    def size(self, key: str) -> int | None:
        return None

    def delete(self, key: str) -> None: ...

    def presign_original(self, profile_id, document_id, expires_in):  # type: ignore[no-untyped-def]
        return None

    def list_prefix(self, prefix: str) -> list[str]:
        return []

    def delete_prefix(self, prefix: str) -> None: ...


@pytest.fixture(scope="module")
def world(pg_url: str) -> Iterator[World]:  # noqa: F811
    mp = pytest.MonkeyPatch()
    mp.setenv("DATABASE_URL", pg_url)
    cfg = Config(str(API_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_DIR / "migrations"))
    command.upgrade(cfg, "head")
    engine = make_engine(pg_url)
    users: dict[str, UUID] = {}
    profiles: dict[str, UUID] = {}
    with engine.begin() as c:
        for sub in SUBS:
            users[sub] = c.execute(
                text("INSERT INTO identity.users (external_sub) VALUES (:s) RETURNING id"),
                {"s": sub},
            ).scalar_one()
            c.execute(
                text(
                    "INSERT INTO identity.consents (user_id, type, terms_version, given_at) "
                    "VALUES (:u, 'research', 'v1', now())"
                ),
                {"u": users[sub]},
            )
            profiles[sub] = c.execute(
                text(
                    "INSERT INTO identity.patient_profiles (owner_user_id) VALUES (:u) RETURNING id"
                ),
                {"u": users[sub]},
            ).scalar_one()
        doc = c.execute(
            text(
                "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime, status) "
                "VALUES (:p, 'k', 'h', 'application/pdf', 'needs_review') RETURNING id"
            ),
            {"p": profiles["alice"]},
        ).scalar_one()
        run = c.execute(
            text(
                "INSERT INTO clinical.extraction_runs (profile_id, document_id, status) "
                "VALUES (:p, :d, 'needs_review') RETURNING id"
            ),
            {"p": profiles["alice"], "d": doc},
        ).scalar_one()
        field = c.execute(
            text(
                "INSERT INTO clinical.extraction_fields "
                "(profile_id, run_id, field_path, value, confidence, source_page) "
                "VALUES (:p, :r, 'a.low', 'synthetic', 0.95, 1) RETURNING id"
            ),
            {"p": profiles["alice"], "r": run},
        ).scalar_one()

    @event.listens_for(engine, "begin")
    def _as_app_rw(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE app_rw")  # RLS applies, like the real login role

    factory = make_session_factory(engine)
    current: dict[str, Principal] = {}

    def make_app(authenticated: bool) -> FastAPI:
        app = create_app()
        for module in (identity_r, doc_r, clinical_r, admin_r, knowledge_r, sharing_r):
            app.dependency_overrides[module.get_session_factory] = lambda: factory
        from medilens.modules.extraction.api import router as ex_r

        app.dependency_overrides[ex_r.get_session_factory] = lambda: factory
        app.dependency_overrides[doc_r.get_storage] = _Storage
        app.dependency_overrides[doc_r.get_dsr_storage] = _Storage
        app.dependency_overrides[doc_r.get_page_images] = _Pages
        limiter = InMemoryLimiter()
        app.dependency_overrides[doc_r.get_limiter] = lambda: limiter
        app.dependency_overrides[knowledge_r.get_allow_drafts] = lambda: True
        app.dependency_overrides[get_token_validator] = lambda: None  # never reached
        if authenticated:  # anonymous keeps the real get_current_user
            app.dependency_overrides[get_current_user] = lambda: current["p"]
        return app

    auth_client = TestClient(make_app(True), raise_server_exceptions=False)
    anon_client = TestClient(make_app(False), raise_server_exceptions=False)

    current["p"] = Principal(sub="alice")
    r = auth_client.post(
        f"/v1/profiles/{profiles['alice']}/shares",
        json={"grantee_user_id": str(users["carol"]), "expires_in_hours": 24},
    )
    assert r.status_code == 201, r.text
    share = r.json()["id"]
    current["p"] = ADMIN_P
    r = auth_client.post(
        "/v1/admin/break-glass",
        json={"profile_id": str(profiles["alice"]), "reason": "Synthetic authz matrix grant"},
    )
    assert r.status_code == 201, r.text
    grant = r.json()["id"]

    ids = {
        "profile_id": str(profiles["alice"]),
        "document_id": str(doc),
        "field_id": str(field),
        "share_id": share,
        "page_no": "1",
        "consent_type": "research",
        "carol": str(users["carol"]),
    }
    yield World({"c": auth_client, "anon": anon_client}, current, ids, grant)
    engine.dispose()
    command.downgrade(cfg, "base")
    mp.undo()


BODIES: dict[Route, dict] = {
    ("DELETE", "/v1/me"): {"confirmation": "wrong phrase"},  # never destructive
    ("POST", "/v1/profiles/{profile_id}/documents"): {
        "content_type": "application/pdf",
        "size_bytes": 1000,
    },
    ("PATCH", "/v1/documents/{document_id}/fields/{field_id}"): {"user_value": "synthetic"},
    ("POST", "/v1/profiles/{profile_id}/reported-findings"): {"text": "synthetic note"},
    ("POST", "/v1/admin/break-glass"): {
        "profile_id": "{profile_id}",
        "reason": "Synthetic authz matrix grant",
    },
    ("POST", "/v1/profiles/{profile_id}/knowledge/search"): {"query": "synthetic", "k": 1},
    ("POST", "/v1/profiles/{profile_id}/shares"): {
        "grantee_user_id": "{carol}",
        "expires_in_hours": 1,
    },
}

PRINCIPALS = {
    "other": Principal(sub="bob"),
    "grantee": Principal(sub="carol"),
    "admin": ADMIN_P,
    "admin+break-glass": ADMIN_P,
    "owner": Principal(sub="alice"),
}


def call(w: World, actor: str, route: Route) -> int:
    method, template = route
    ids = dict(w.ids)
    ids["grant_id"] = w.grant_id if actor == "admin+break-glass" else str(uuid4())
    path = re.sub(r"\{(\w+)\}", lambda m: ids[m.group(1)], template)
    body = BODIES.get(route)
    if body is not None:
        body = {k: ids.get(v.strip("{}"), v) if isinstance(v, str) else v for k, v in body.items()}
    if actor == "anonymous":
        client = w.clients["anon"]
    else:
        w.current["p"] = PRINCIPALS[actor]
        client = w.clients["c"]
    r = client.request(method, path, json=body)
    if r.status_code in {401, 403, 404}:  # SEC: denials are Problem Details, never HTML/empty
        assert r.headers["content-type"].startswith("application/problem+json"), (
            actor,
            route,
            r.text,
        )
    return r.status_code


def test_authorisation_matrix(world: World) -> None:
    """(a) anonymous 401; (b) other user, grantee, admin get 403/404 on someone else's data."""
    observed: dict[Route, dict[str, int]] = {r: {} for r in ROUTES}
    for actor in RUN_ORDER:
        for route in ROUTES:
            observed[route][actor] = call(world, actor, route)
    failures = [
        f"{m} {p} as {a}: got {observed[(m, p)][a]}, want {expected(cls, a)}"
        for (m, p), cls in ROUTES.items()
        for a in ACTORS
        if not matches(expected(cls, a), observed[(m, p)][a])
    ]
    out = os.environ.get("AUTHZ_MATRIX_OUT")
    if out:
        Path(out).write_text(render(observed))
    assert not failures, "\n".join(failures)


def test_public_routes_need_no_token(world: World) -> None:
    for method, path in PUBLIC:
        assert world.clients["anon"].request(method, path).status_code == 200, path


SERVICE_ROUTES = """

## Service-to-service routes (not in the API app)

These are separate FastAPI apps authenticated with short-lived HMAC service tokens
(`docs/architecture/service-auth.md`), not user tokens, so they have no owner/other/grantee
actors. Observed by their own suites, not by this generator.

| Service | Route | Anonymous / bad token | Valid service token | Tests |
|---|---|---|---|---|
| ai-gateway | `GET /healthz` | 200 (public probe) | 200 | `apps/ai-gateway/tests` |
| ai-gateway | `POST /v1/complete` | 401 (missing, garbage, expired, wrong audience, tampered, wrong secret, secret unset) | 200 inside token scope; 403 when `tenant_id`/`profile_id` is not in the token claims | `test_gateway.py::test_bad_token_401`, `test_secret_unset_fails_closed`, scope cases |
| phi-service | `GET /healthz` | 200 (public probe) | 200 | `apps/phi-service/tests/test_health.py` |
| phi-service | `POST /v1/subjects` | 401 (same bad-token set, replay, secret unset) | 201 | `test_phi.py::test_unauthorized`, `test_replayed_token_rejected`, `test_no_token_configured_denies_all` |
| phi-service | `GET /v1/subjects/{key}` | 401 | 200 | same |
| phi-service | `DELETE /v1/subjects/{key}` | 401 | 204 | same |

No test was missing, so none was added.
"""


def render(observed: dict[Route, dict[str, int]]) -> str:
    head = (
        "# Authorisation matrix (generated)\n\n"
        "Generated by `AUTHZ_MATRIX_OUT=docs/qa/authz-matrix.md uv run pytest tests/authz` in "
        "`apps/api`. Cells show `observed status` and a tick when it meets the expectation of the "
        "route class. `deny` = 403/404; `allow` = authorised (any status other than 401/403/404/5xx, "
        "e.g. 200/201/204 or a business 4xx).\n\n"
        "| Route | Class | " + " | ".join(ACTORS) + " |\n|---|---|" + "---|" * len(ACTORS) + "\n"
    )
    rows = []
    for (m, p), cls in ROUTES.items():
        cells = [
            f"{observed[(m, p)][a]} (want {expected(cls, a)}) "
            + ("ok" if matches(expected(cls, a), observed[(m, p)][a]) else "FAIL")
            for a in ACTORS
        ]
        rows.append(f"| `{m} {p}` | {cls} | " + " | ".join(cells) + " |")
    pub = "\n".join(f"| `{m} {p}` | {why} |" for (m, p), why in PUBLIC.items())
    return (
        head
        + "\n".join(rows)
        + "\n\n## Public allow-list\n\n| Route | Reason |\n|---|---|\n"
        + pub
        + SERVICE_ROUTES
    )
