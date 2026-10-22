from __future__ import annotations

import json
import logging
import secrets

from medilens_phi.crypto import Encryptor
from medilens_phi.repository import SubjectRecord, SubjectRepository

audit = logging.getLogger("medilens_phi.audit")

PHI_FIELDS = ("display_name", "birth_date", "phone", "email")


class SubjectNotFound(Exception):
    pass


def _aad(subject_key: str, field: str = "") -> bytes:
    return f"{subject_key}|{field}".encode()


class SubjectService:
    def __init__(self, repo: SubjectRepository, encryptor: Encryptor) -> None:
        self._repo = repo
        self._enc = encryptor

    def create(self, values: dict[str, str | None]) -> str:
        key = "sub_" + secrets.token_urlsafe(24)
        dek = self._enc.new_data_key()
        fields = {
            name: self._enc.encrypt(dek, json.dumps(v).encode(), _aad(key, name))
            for name, v in values.items()
            if name in PHI_FIELDS and v is not None
        }
        self._repo.add(SubjectRecord(key, self._enc.wrap(dek, _aad(key)), fields))
        audit.info("phi.create subject_key=%s", key)
        return key

    def get(self, key: str) -> dict[str, str | None]:
        rec = self._repo.get(key)
        if rec is None:
            audit.info("phi.read subject_key=%s outcome=not_found", key)
            raise SubjectNotFound(key)
        dek = self._enc.unwrap(rec.wrapped_data_key, _aad(key))
        out: dict[str, str | None] = dict.fromkeys(PHI_FIELDS)
        for name, blob in rec.fields.items():
            out[name] = json.loads(self._enc.decrypt(dek, blob, _aad(key, name)))
        audit.info("phi.read subject_key=%s outcome=ok", key)
        return out

    def shred(self, key: str) -> None:
        """Crypto-shred: removing the wrapped data key (and row) makes ciphertext unrecoverable."""
        if not self._repo.delete(key):
            audit.info("phi.shred subject_key=%s outcome=not_found", key)
            raise SubjectNotFound(key)
        audit.info("phi.shred subject_key=%s outcome=ok", key)
