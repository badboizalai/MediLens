from uuid import UUID

from medilens.modules.knowledge.domain.models import (
    Chunk,
    Embedder,
    Hit,
    KnowledgeRepository,
    ProfileNotFound,
    chunk_article,
    split_text,
)

MAX_K = 10


class KnowledgeService:
    """The caller commits the DB transaction."""

    def __init__(
        self, repo: KnowledgeRepository, embedder: Embedder, allow_drafts: bool = False
    ) -> None:
        self._repo = repo
        self._emb = embedder
        self._drafts = allow_drafts

    def ingest_article(self, raw: str) -> str:
        article_id, chunks = chunk_article(raw)
        self._repo.replace_article(article_id, [(c, self._emb.embed(c.content)) for c in chunks])
        return article_id

    def index_profile_text(self, profile_id: UUID, text: str, source_ref: str) -> None:
        """Trusted internal callers only (e.g. after a confirmed extraction): no ownership check."""
        chunks = [Chunk(c, source_ref=source_ref, reviewed=True) for c in split_text(text)]
        self._repo.replace_profile_text(
            profile_id, source_ref, [(c, self._emb.embed(c.content)) for c in chunks]
        )

    def search(self, subject: str, profile_id: UUID, query: str, k: int) -> list[Hit]:
        user = self._repo.resolve(subject)
        if user is None or not self._repo.owns(user, profile_id):
            raise ProfileNotFound
        k = max(1, min(k, MAX_K))
        # Explicit profile filter in the repo query AND RLS (D95): either alone must hold.
        return self._repo.search(profile_id, self._emb.embed(query), k, self._drafts)
