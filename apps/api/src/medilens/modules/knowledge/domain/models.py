"""Pure knowledge domain: article parsing, chunking, ports. No I/O."""

import re
from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import UUID

from medilens.core.errors import NotFound

MAX_CHARS = 800
LANGS = {"Tiếng Việt": "vi", "English": "en"}


class ProfileNotFound(NotFound):
    """Raised for unknown AND foreign profiles alike: no existence oracle."""


@dataclass(frozen=True)
class Chunk:
    content: str
    article_id: str | None = None
    language: str | None = None
    title: str | None = None
    citations: list[dict[str, str]] = field(default_factory=list)
    reviewed: bool = False
    source_ref: str | None = None


@dataclass(frozen=True)
class Hit:
    content: str
    article_id: str | None
    language: str | None
    title: str | None
    citations: list[dict[str, Any]]
    profile_id: UUID | None
    distance: float


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


class KnowledgeRepository(Protocol):
    def resolve(self, subject: str) -> UUID | None: ...
    def owns(self, user_id: UUID, profile_id: UUID) -> bool: ...
    def replace_article(self, article_id: str, chunks: list[tuple[Chunk, list[float]]]) -> None: ...
    def replace_profile_text(
        self, profile_id: UUID, source_ref: str, chunks: list[tuple[Chunk, list[float]]]
    ) -> None: ...
    def search(
        self, profile_id: UUID, vector: list[float], k: int, allow_drafts: bool
    ) -> list[Hit]: ...


def split_text(text: str, limit: int = MAX_CHARS) -> list[str]:
    """Pack paragraphs up to `limit` chars; an oversize paragraph is cut on whitespace."""
    out: list[str] = []
    cur = ""
    for para in (p.strip() for p in re.split(r"\n\s*\n", text)):
        while len(para) > limit:
            cut = para.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            if cur:
                out.append(cur)
                cur = ""
            out.append(para[:cut].strip())
            para = para[cut:].strip()
        if not para:
            continue
        if cur and len(cur) + 2 + len(para) > limit:
            out.append(cur)
            cur = para
        else:
            cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        out.append(cur)
    return out


def _unquote(v: str) -> str:
    return v.strip().strip('"')


def _front_matter(raw: str) -> tuple[dict[str, Any], str]:
    """Minimal parser for our article header: scalars plus `sources` as a list of mappings."""
    _, head, body = raw.split("---\n", 2)
    meta: dict[str, Any] = {}
    key = ""
    for line in head.splitlines():
        if m := re.match(r"^(\w+):\s*(.*)$", line):
            key, val = m.group(1), _unquote(m.group(2))
            meta[key] = [] if val == "" else (None if val == "null" else val)
        elif key == "sources" and (m := re.match(r"^  - (\w+):\s*(.*)$", line)):
            meta[key].append({m.group(1): _unquote(m.group(2))})
        elif key == "sources" and (m := re.match(r"^    (\w+):\s*(.*)$", line)):
            meta[key][-1][m.group(1)] = _unquote(m.group(2))
    return meta, body


def chunk_article(raw: str) -> tuple[str, list[Chunk]]:
    """Split a KnowledgeArticle markdown file into per-language chunks that carry citations."""
    meta, body = _front_matter(raw)
    article_id = meta["id"]
    citations = [
        {"title": s.get("title", ""), "url": s.get("url", "")} for s in meta.get("sources", [])
    ]
    reviewed = bool(meta.get("cso_review_date"))  # BR-024/BR-051
    chunks: list[Chunk] = []
    for section in re.split(r"^## ", body, flags=re.M)[1:]:
        heading, _, text = section.partition("\n")
        lang = LANGS.get(heading.strip())
        if lang is None:
            continue
        title = meta.get(f"title_{lang}")
        chunks += [Chunk(c, article_id, lang, title, citations, reviewed) for c in split_text(text)]
    return article_id, chunks
