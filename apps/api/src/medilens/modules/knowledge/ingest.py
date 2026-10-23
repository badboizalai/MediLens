"""Ingest KnowledgeArticles: `python -m medilens.modules.knowledge.ingest content/articles`.

Needs a role allowed to write public chunks (migrator/superuser via DATABASE_URL).
"""

import sys
from pathlib import Path

from sqlalchemy.orm import Session

from medilens.core.db import make_engine
from medilens.modules.knowledge.application.service import KnowledgeService
from medilens.modules.knowledge.infra.hashing_embedder import HashingEmbedder
from medilens.modules.knowledge.infra.sql_repository import SqlKnowledgeRepository


def ingest_dir(session: Session, directory: Path) -> list[str]:
    service = KnowledgeService(SqlKnowledgeRepository(session), HashingEmbedder())
    return [service.ingest_article(p.read_text("utf-8")) for p in sorted(directory.glob("KA-*.md"))]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python -m medilens.modules.knowledge.ingest <articles-dir>")
        return 2
    with Session(make_engine()) as session, session.begin():
        ids = ingest_dir(session, Path(argv[1]))
    print(f"ingested {len(ids)} articles")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
