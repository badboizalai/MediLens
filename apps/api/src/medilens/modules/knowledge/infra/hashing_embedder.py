import hashlib
import re


class HashingEmbedder:
    """Deterministic bag-of-words embedder for dev/tests. Needs no model and no network.

    shortcut: lexical overlap only, not semantic; replace with Bedrock Titan/Cohere embeddings
    via ai-gateway (new vector column + reindex) before real use.
    """

    DIM = 256

    def embed(self, text: str) -> list[float]:
        v = [0.0] * self.DIM
        for tok in re.findall(r"\w+", text.lower()):
            h = int.from_bytes(hashlib.blake2b(tok.encode(), digest_size=8).digest(), "big")
            v[h % self.DIM] += 1.0 if (h >> 32) & 1 else -1.0
        norm = sum(x * x for x in v) ** 0.5
        if norm == 0:
            v[0] = 1.0  # cosine distance is undefined for the zero vector
            return v
        return [x / norm for x in v]
