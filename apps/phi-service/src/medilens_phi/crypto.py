"""Envelope encryption primitives (SEC-AR). Cloud: swap AesGcmEncryptor for a KMS-backed one."""

from __future__ import annotations

import os
from typing import Protocol

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_NONCE = 12


class DecryptionError(Exception):
    """Ciphertext failed authentication (tampered, wrong key or wrong context)."""


class Encryptor(Protocol):
    def new_data_key(self) -> bytes: ...
    def wrap(self, data_key: bytes, aad: bytes) -> bytes: ...
    def unwrap(self, wrapped: bytes, aad: bytes) -> bytes: ...
    def encrypt(self, data_key: bytes, plaintext: bytes, aad: bytes) -> bytes: ...
    def decrypt(self, data_key: bytes, blob: bytes, aad: bytes) -> bytes: ...


def _seal(key: bytes, plaintext: bytes, aad: bytes) -> bytes:
    nonce = os.urandom(_NONCE)
    return nonce + AESGCM(key).encrypt(nonce, plaintext, aad)


def _open(key: bytes, blob: bytes, aad: bytes) -> bytes:
    try:
        return AESGCM(key).decrypt(blob[:_NONCE], blob[_NONCE:], aad)
    except (InvalidTag, ValueError) as exc:
        raise DecryptionError("authentication failed") from exc


class AesGcmEncryptor:
    """Local-dev implementation: the KEK comes from env, data keys are random AES-256."""

    def __init__(self, kek: bytes) -> None:
        if len(kek) != 32:
            raise ValueError("KEK must be 32 bytes")
        self._kek = kek

    def new_data_key(self) -> bytes:
        return AESGCM.generate_key(bit_length=256)

    def wrap(self, data_key: bytes, aad: bytes) -> bytes:
        return _seal(self._kek, data_key, aad)

    def unwrap(self, wrapped: bytes, aad: bytes) -> bytes:
        return _open(self._kek, wrapped, aad)

    def encrypt(self, data_key: bytes, plaintext: bytes, aad: bytes) -> bytes:
        return _seal(data_key, plaintext, aad)

    def decrypt(self, data_key: bytes, blob: bytes, aad: bytes) -> bytes:
        return _open(data_key, blob, aad)
