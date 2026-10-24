"""Export, consent withdrawal and account erasure (T106). Commits its own transaction."""

import hashlib
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from medilens.modules.identity.domain.dsr import (
    ConsentNotFound,
    DsrRepository,
    ProfileStore,
    UserNotFound,
)


class ErasureIncomplete(RuntimeError):
    """verify_erased found leftovers; nothing was committed."""


class DsrService:
    def __init__(self, repo: DsrRepository, stores: Sequence[ProfileStore]) -> None:
        # Order matters for erasure: dependants first (extraction before documents).
        self._repo, self._stores = repo, stores

    def _user(self, subject: str) -> UUID:
        user = self._repo.resolve(subject)
        if user is None:
            raise UserNotFound("Account not found.")
        return user

    def export(self, subject: str) -> dict[str, Any]:
        user = self._user(subject)
        profiles = self._repo.profiles(user)
        self._repo.scope_to([p["id"] for p in profiles])
        bundle: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc),
            "user_id": user,
            "consents": self._repo.consents(user),
            "profiles": [
                {**p, **{k: v for s in self._stores for k, v in s.export_profile(p["id"]).items()}}
                for p in profiles
            ],
        }
        self._repo.audit(user, "dsr.export", None)
        self._repo.commit()
        return bundle

    def withdraw(self, subject: str, consent_type: str) -> datetime:
        user = self._user(subject)
        at = self._repo.withdraw(user, consent_type)
        if at is None:
            raise ConsentNotFound("No such consent.")
        self._repo.audit(user, "dsr.consent_withdraw", None)
        self._repo.commit()
        return at

    def erase(self, subject: str) -> UUID:
        """Idempotent: a repeat after success returns the original receipt."""
        digest = hashlib.sha256(subject.encode()).hexdigest()
        user = self._repo.resolve(subject)
        if user is None:
            receipt = self._repo.receipt_for(digest)
            if receipt is None:
                raise UserNotFound("Account not found.")
            return receipt
        pids = [p["id"] for p in self._repo.profiles(user)]
        self._repo.scope_to(pids)
        for pid in pids:
            for store in self._stores:
                store.erase_profile(pid)
        receipt = self._repo.new_id()
        self._repo.erase_user(user, str(receipt))
        left = self.verify_erased(user, pids)
        if left:  # not committed: the transaction rolls back and the request can be retried
            raise ErasureIncomplete(", ".join(left))
        self._repo.add_receipt(receipt, digest, {"profiles": len(pids)})
        self._repo.audit(None, "dsr.erase", receipt)
        self._repo.commit()
        return receipt

    def verify_erased(self, user_id: UUID, profile_ids: list[UUID]) -> list[str]:
        """Everything still holding the user's data; empty means erased. Audit events survive
        by design, with actor ids pseudonymised (checked here too)."""
        left = self._repo.leftovers(user_id, profile_ids)
        for store in self._stores:
            left += store.leftovers(profile_ids)
        return left
