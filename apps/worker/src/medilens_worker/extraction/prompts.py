"""Prompt loading and rendering for extract-v1 (files live in ml/prompts)."""

import json
from pathlib import Path

PROMPT_VERSION = "extract-v2"
V1 = "extract-v1"  # kept for comparison: no line ids, no few-shots
UNITS = ("dental", "cardiology", "oncology")


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "ml" / "prompts").is_dir():
            return p
    raise FileNotFoundError("ml/prompts not found")


ROOT = _repo_root()
PROMPTS = ROOT / "ml" / "prompts"
SCHEMA_DIR = ROOT / "ml" / "schemas"


def load_schemas() -> dict[str, dict]:
    """Unit name (and 'common') -> schema."""
    return {
        p.name.split(".")[0]: json.loads(p.read_text("utf-8")) for p in SCHEMA_DIR.glob("*.v1.json")
    }


def neutralise(text: str) -> str:
    """Document text is data: it must not be able to close our delimiter tag."""
    return text.replace("<document_text", "<\\document_text").replace(
        "</document_text", "<\\/document_text"
    )


def render_pages(pages: list[str], line_ids: bool = False) -> str:
    """line_ids: prefix each line [L<n>] (1-based per page) so the model cites lines, not boxes."""

    def body(t: str) -> str:
        t = neutralise(t)
        return "\n".join(f"[L{n}] {x}" for n, x in enumerate(t.split("\n"), 1)) if line_ids else t

    return "\n".join(f"[[page {i}]]\n{body(t)}" for i, t in enumerate(pages, 1))


def _t(name: str, version: str = PROMPT_VERSION) -> str:
    return (PROMPTS / version / name).read_text("utf-8")


def classify_prompt(pages: list[str]) -> str:
    user = _t("classify.user.txt").format(
        units=json.dumps(list(UNITS)), document_text=render_pages(pages, line_ids=True)[:1500]
    )
    return f"{_t('system.txt')}\n\n{user}"


def extract_prompt(
    unit: str,
    schema: dict,
    pages: list[str],
    errors: list[str] | None = None,
    version: str = PROMPT_VERSION,
) -> str:
    v2 = version != V1
    user = _t("extract.user.txt", version).format(
        unit_code=unit,
        schema_json=json.dumps(schema, ensure_ascii=False),
        document_text=render_pages(pages, line_ids=v2),
        examples=_t(f"examples/{unit}.txt", version) if v2 else "",
    )
    prompt = f"{_t('system.txt', version)}\n\n{user}"
    if errors:
        prompt += "\n" + _t("repair.user.txt", version).format(errors="\n".join(errors[:10]))
    return prompt
