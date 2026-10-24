"""SEC-AP-08 / F7: per-user upload rate, daily quota and concurrent SSE stream cap."""

import pytest
from medilens.core.config import get_settings
from medilens.modules.document.api import router as doc_router
from medilens.modules.document.application.rate_limit import DAY, MINUTE, InMemoryLimiter

from .conftest import Env
from .test_status_stream import FakeClock
from .test_upload import request


class Now:
    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t


def test_hit_allows_denies_and_rolls_over() -> None:
    now = Now()
    lim = InMemoryLimiter(now)
    assert [lim.hit("k", 2, MINUTE) for _ in range(2)] == [None, None]
    assert lim.hit("k", 2, MINUTE) == pytest.approx(MINUTE)
    assert lim.hit("other", 2, MINUTE) is None  # keys are independent
    now.t += 59
    assert lim.hit("k", 2, MINUTE) == pytest.approx(1)  # denied hits are not recorded
    now.t += 1
    assert lim.hit("k", 2, MINUTE) is None  # window rolled over


def test_acquire_release() -> None:
    lim = InMemoryLimiter()
    assert [lim.acquire("s", 2) for _ in range(3)] == [True, True, False]
    lim.release("s")
    assert lim.acquire("s", 2)
    for _ in range(3):
        lim.release("s")  # never negative
    assert lim.acquire("s", 1)


def test_upload_rate_limit_is_429_with_retry_after(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "upload_requests_per_minute", 2)
    now = Now()
    env.limiter._now = now
    assert [request(env).status_code for _ in range(2)] == [201, 201]
    r = request(env)
    assert r.status_code == 429
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.headers["retry-after"] == str(int(MINUTE))
    env.as_user("bob")  # keyed by subject
    assert request(env, profile=env.bob_profile).status_code == 201
    env.as_user("alice")
    now.t += MINUTE
    assert request(env).status_code == 201


def test_daily_quota_is_429_until_the_day_rolls_over(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "upload_daily_quota", 2)
    now = Now()
    env.limiter._now = now
    assert request(env).status_code == 201
    now.t += MINUTE + 1
    assert request(env).status_code == 201
    now.t += MINUTE + 1
    r = request(env)
    assert r.status_code == 429
    assert int(r.headers["retry-after"]) > MINUTE
    now.t += DAY
    assert request(env).status_code == 201


def test_sse_cap_is_429_and_slot_is_released_after_stream(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "sse_max_streams_per_user", 1)
    doc_id = request(env).json()["document_id"]
    env.client.app.dependency_overrides[doc_router.get_clock] = FakeClock().clock  # type: ignore[attr-defined]
    assert env.limiter.acquire("sse:alice", 1)  # another open stream
    r = env.client.get(f"/v1/documents/{doc_id}/events")
    assert r.status_code == 429
    assert r.headers["retry-after"]
    env.limiter.release("sse:alice")
    # the stream runs to its max duration on the fake clock, then must free its slot
    assert env.client.get(f"/v1/documents/{doc_id}/events").status_code == 200
    assert env.limiter.acquire("sse:alice", 1)
