"""Load golden-v0 pages: one page per record (degraded variant when it exists, else clean).

Reference text is not stored in golden-v0 itself; `make_reference` re-emits it from the
seeded generator into reference/golden-v0.reference.jsonl (synthetic text only).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_REFERENCE = (
    Path(__file__).resolve().parent.parent / "reference" / "golden-v0.reference.jsonl"
)


@dataclass(frozen=True)
class Page:
    doc_id: str
    image: Path
    lang: str
    quality: str
    unit: str
    reference: str


def load_reference(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8") as f:
        return {r["doc_id"]: r["text"] for r in map(json.loads, filter(str.strip, f))}


def load_pages(golden: Path, reference: Path = DEFAULT_REFERENCE) -> list[Page]:
    refs = load_reference(reference)
    pages = []
    with (golden / "gold.jsonl").open(encoding="utf-8") as f:
        for row in map(json.loads, filter(str.strip, f)):
            doc_id = row["doc_id"]
            rec = json.loads((golden / "records" / f"{doc_id}.json").read_text(encoding="utf-8"))
            images = {i["variant"]: i["file"] for i in rec["metadata"]["images"]}
            rel = images.get("degraded") or images["clean"]
            pages.append(
                Page(
                    doc_id=doc_id,
                    image=golden / rel,
                    lang=rec["metadata"]["lang"],
                    quality=row["quality"],
                    unit=row["unit"],
                    reference=refs[doc_id],
                )
            )
    return pages
