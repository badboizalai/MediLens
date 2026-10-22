"""Validate an OIDC access token and map it to a Principal (API only validates; PKCE lives in web/BFF)."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import jwt

from medilens.modules.identity.domain.principal import InvalidToken, Principal

# Resolves the signing key for a token's `kid`; raises KeyError if unknown.
KeyResolver = Callable[[str], Any]


@dataclass(frozen=True)
class ValidatorConfig:
    issuer: str
    audience: str
    algorithms: tuple[str, ...] = ("RS256",)
    roles_claims: tuple[str, ...] = ("realm_access.roles", "cognito:groups", "roles")
    leeway_seconds: int = 30


def _dig(claims: dict[str, Any], path: str) -> Any:
    if path in claims:  # literal key, e.g. "cognito:groups"
        return claims[path]
    cur: Any = claims
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


class TokenValidator:
    def __init__(self, config: ValidatorConfig, resolve_key: KeyResolver) -> None:
        self._cfg = config
        self._resolve_key = resolve_key

    def validate(self, token: str) -> Principal:
        cfg = self._cfg
        try:
            header = jwt.get_unverified_header(token)
            alg = header.get("alg")
            kid = header.get("kid")
            if alg not in cfg.algorithms or not kid:  # blocks alg=none / HS confusion
                raise InvalidToken("unsupported alg or missing kid")
            claims = jwt.decode(
                token,
                key=self._resolve_key(kid),
                algorithms=list(cfg.algorithms),
                issuer=cfg.issuer,
                audience=cfg.audience,
                leeway=cfg.leeway_seconds,
                options={"require": ["exp", "iss", "sub"]},
            )
        except InvalidToken:
            raise
        except (jwt.PyJWTError, KeyError, ValueError) as exc:
            raise InvalidToken(type(exc).__name__) from exc
        return Principal(sub=str(claims["sub"]), roles=self._roles(claims))

    def _roles(self, claims: dict[str, Any]) -> frozenset[str]:
        found: set[str] = set()
        for path in self._cfg.roles_claims:
            value = _dig(claims, path)
            if isinstance(value, list):
                found.update(str(v) for v in value)
        return frozenset(found)
