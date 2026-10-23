"""Semantic cache for explanation (Q&A) answers (D97). Per-profile scope: never shared across users."""

import re
import unicodedata
from collections import OrderedDict
from collections.abc import Callable
from typing import Generic, TypeVar

SIMILARITY_THRESHOLD = 0.85  # token-set Jaccard; below this a question is treated as new
MAX_ENTRIES = 1000
TTL_S = 3600

V = TypeVar("V")


def normalise(text: str) -> frozenset[str]:
    """Lowercase, strip diacritics/punctuation, collapse spaces -> token set."""
    t = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return frozenset(re.sub(r"[^a-z0-9]+", " ", t).split())


def similarity(a: frozenset[str], b: frozenset[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


class SemanticCache(Generic[V]):
    """In-memory. Swap for Redis/ElastiCache behind the same get/put to share across tasks.

    shortcut: token-set Jaccard + linear scan, not embeddings; upgrade to embeddings +
    pgvector/OpenSearch k-NN when paraphrase hit-rate matters.
    """

    def __init__(
        self,
        clock: Callable[[], float],
        ttl_s: float = TTL_S,
        max_entries: int = MAX_ENTRIES,
        threshold: float = SIMILARITY_THRESHOLD,
    ) -> None:
        self._clock, self._ttl, self._max, self._threshold = clock, ttl_s, max_entries, threshold
        self._items: OrderedDict[tuple[tuple[str, ...], frozenset[str]], tuple[float, V]] = (
            OrderedDict()
        )
        self.hits = 0
        self.misses = 0

    def get(self, scope: tuple[str, ...], question: str) -> V | None:
        toks, now = normalise(question), self._clock()
        best: tuple[float, V] | None = None
        for key, (ts, v) in list(self._items.items()):
            if now - ts >= self._ttl:
                del self._items[key]
            elif key[0] == scope and (sim := similarity(toks, key[1])) >= self._threshold:
                if best is None or sim > best[0]:
                    best = (sim, v)
        if best is None:
            self.misses += 1
            return None
        self.hits += 1
        return best[1]

    def put(self, scope: tuple[str, ...], question: str, value: V) -> None:
        key = (scope, normalise(question))
        self._items.pop(key, None)
        self._items[key] = (self._clock(), value)
        while len(self._items) > self._max:
            self._items.popitem(last=False)
