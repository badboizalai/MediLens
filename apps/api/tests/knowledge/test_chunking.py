from medilens.modules.knowledge.domain.models import MAX_CHARS, chunk_article, split_text
from medilens.modules.knowledge.infra.hashing_embedder import HashingEmbedder

from .conftest import ARTICLES

RAW = """---
id: KA-999
title_vi: "Tiêu đề"
title_en: "Title"
sources:
  - title: "WHO"
    url: https://example.org/a
cso_review_date: null
---

## Tiếng Việt

Đoạn một.

Đoạn hai.

## English

Para one.
"""


def test_article_chunks_carry_metadata() -> None:
    aid, chunks = chunk_article(RAW)
    assert aid == "KA-999"
    assert [(c.language, c.title, c.content) for c in chunks] == [
        ("vi", "Tiêu đề", "Đoạn một.\n\nĐoạn hai."),
        ("en", "Title", "Para one."),
    ]
    assert chunks[0].citations == [{"title": "WHO", "url": "https://example.org/a"}]
    assert not chunks[0].reviewed
    assert chunk_article(RAW.replace("null", "2026-11-01"))[1][0].reviewed


def test_split_respects_limit() -> None:
    long = " ".join(["word"] * 500)
    parts = split_text(f"{long}\n\nshort")
    assert all(len(p) <= MAX_CHARS for p in parts) and len(parts) >= 3


def test_real_articles_parse() -> None:
    paths = list(ARTICLES.glob("KA-*.md"))
    assert len(paths) == 20
    for p in paths:
        aid, chunks = chunk_article(p.read_text("utf-8"))
        assert aid == p.stem
        assert {c.language for c in chunks} == {"vi", "en"}
        assert all(c.citations and len(c.content) <= MAX_CHARS for c in chunks)


def test_embedder_deterministic_unit_norm() -> None:
    e = HashingEmbedder()
    v = e.embed("răng hàm FDI")
    assert v == e.embed("răng hàm FDI") and len(v) == 256
    assert abs(sum(x * x for x in v) - 1) < 1e-9
    assert len(e.embed("!!!")) == 256
