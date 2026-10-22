"""Prompt loading and rendering for extract-v1 (files live in ml/prompts)."""

import json
from pathlib import Path

PROMPT_VERSION = "extract-v1"
UNITS = ("dental", "cardiology", "oncology")


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "ml" / "prompts").is_dir():
            return p
    raise FileNotFoundError("ml/prompts not found")


ROOT = _repo_root()
PROMPT_DIR = ROOT / "ml" / "prompts" / PROMPT_VERSION
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


def render_pages(pages: list[str]) -> str:
    return "\n".join(f"[[page {i}]]\n{neutralise(t)}" for i, t in enumerate(pages, 1))


def _t(name: str) -> str:
    return (PROMPT_DIR / name).read_text("utf-8")


def classify_prompt(pages: list[str]) -> str:
    user = _t("classify.user.txt").format(
        units=json.dumps(list(UNITS)), document_text=render_pages(pages)[:1500]
    )
    return f"{_t('system.txt')}\n\n{user}"


def extract_prompt(
    unit: str, schema: dict, pages: list[str], errors: list[str] | None = None
) -> str:
    user = _t("extract.user.txt").format(
        unit_code=unit,
        schema_json=json.dumps(schema, ensure_ascii=False),
        document_text=render_pages(pages),
    )
    prompt = f"{_t('system.txt')}\n\n{user}"
    if errors:
        prompt += "\n" + _t("repair.user.txt").format(errors="\n".join(errors[:10]))
    return prompt
