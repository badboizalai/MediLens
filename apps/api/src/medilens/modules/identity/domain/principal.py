"""Authenticated caller. Pure domain: no framework or IdP types."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    sub: str
    roles: frozenset[str] = frozenset()

    def has_role(self, *roles: str) -> bool:
        return bool(self.roles.intersection(roles))


class InvalidToken(Exception):
    """Token missing, malformed, expired, or failing signature/iss/aud checks."""
