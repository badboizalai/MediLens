"""Short-lived HMAC service tokens (see docs/architecture/service-auth.md).

Duplicated per app on purpose (no cross-app imports): keep copies identical.

Wire format: ``b64url(json claims) "." b64url(HMAC-SHA256(secret, first part))``.
Claims: iss (caller id), aud, iat, exp, nonce; optional tenants/profiles (scope).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import threading
import time
from typing import Any

MAX_TTL_S = 300
_SKEW_S = 30


class TokenError(Exception):
    """Token missing, malformed, forged, expired, wrong audience or replayed."""


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _sign(secret: str, payload: str) -> str:
    return _b64(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())


def mint(
    secret: str,
    *,
    caller: str,
    audience: str,
    ttl_s: int = 60,
    tenants: list[str] | None = None,
    profiles: list[str] | None = None,
    now: float | None = None,
) -> str:
    if not secret:
        raise ValueError("secret required")
    if not 0 < ttl_s <= MAX_TTL_S:
        raise ValueError(f"ttl_s must be 1..{MAX_TTL_S}")
    iat = int(now if now is not None else time.time())
    claims: dict[str, Any] = {
        "iss": caller,
        "aud": audience,
        "iat": iat,
        "exp": iat + ttl_s,
        "nonce": secrets.token_urlsafe(12),
    }
    if tenants is not None:
        claims["tenants"] = tenants
    if profiles is not None:
        claims["profiles"] = profiles
    payload = _b64(json.dumps(claims, separators=(",", ":")).encode())
    return f"{payload}.{_sign(secret, payload)}"


class Verifier:
    """Verifies tokens for one audience; rejects replayed nonces within their lifetime."""

    def __init__(self, secret: str, audience: str) -> None:
        self.secret = secret
        self._aud = audience
        self._seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def verify(self, token: str, *, now: float | None = None) -> dict[str, Any]:
        if not self.secret:  # fail closed
            raise TokenError("service auth not configured")
        t = now if now is not None else time.time()
        try:
            payload, sig = token.split(".")
            if not hmac.compare_digest(sig, _sign(self.secret, payload)):
                raise TokenError("bad signature")
            claims = json.loads(_unb64(payload))
            exp, iat = int(claims["exp"]), int(claims["iat"])
            nonce, iss = str(claims["nonce"]), str(claims["iss"])
        except TokenError:
            raise
        except Exception as e:  # malformed input of any kind
            raise TokenError("malformed token") from e
        if claims.get("aud") != self._aud:
            raise TokenError("wrong audience")
        if not iss or not nonce:
            raise TokenError("malformed token")
        if exp <= t or exp - iat > MAX_TTL_S or iat > t + _SKEW_S:
            raise TokenError("expired or invalid lifetime")
        with self._lock:
            self._seen = {n: e for n, e in self._seen.items() if e > t}
            if nonce in self._seen:
                raise TokenError("replayed nonce")
            self._seen[nonce] = exp
        return claims


def bearer(header: str) -> str:
    scheme, _, tok = header.partition(" ")
    if scheme.lower() != "bearer" or not tok:
        raise TokenError("missing bearer token")
    return tok
