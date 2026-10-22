"""Extraction orchestration: classify -> extract -> validate (+1 repair) -> cite-check."""

import json
import re
from dataclasses import dataclass, field
from typing import Protocol
from urllib import request as urlrequest

from .jsonschema_lite import Validator
from .prompts import PROMPT_VERSION, UNITS, classify_prompt, extract_prompt, load_schemas


class ExtractionError(Exception):
    """Output unusable after the repair retry (job fails / goes to review)."""


@dataclass(frozen=True)
class Completion:
    text: str
    model: str
    cost_usd: float


class GatewayClient(Protocol):
    """The only way this package reaches an LLM: the AI Gateway."""

    def complete(self, prompt: str, *, max_output_tokens: int = 4096) -> Completion: ...


class HttpGatewayClient:
    """POST {base_url}/v1/complete (apps/ai-gateway)."""

    def __init__(
        self, base_url: str, tenant_id: str, profile_id: str = "extract", timeout: float = 60
    ) -> None:
        self._url = base_url.rstrip("/") + "/v1/complete"
        self._tenant, self._profile, self._timeout = tenant_id, profile_id, timeout

    def complete(self, prompt: str, *, max_output_tokens: int = 4096) -> Completion:
        body = json.dumps(
            {
                "tenant_id": self._tenant,
                "profile_id": self._profile,
                "prompt": prompt,
                "max_output_tokens": max_output_tokens,
            }
        ).encode()
        req = urlrequest.Request(self._url, body, {"Content-Type": "application/json"})  # noqa: S310 - fixed internal URL
        with urlrequest.urlopen(req, timeout=self._timeout) as r:  # noqa: S310 - fixed internal URL
            d = json.load(r)
        return Completion(d["text"], d["model"], float(d["cost_usd"]))


@dataclass
class ExtractionRun:
    document_id: str
    unit: str
    model: str
    prompt_version: str
    cost_usd: float
    confidence: float
    result: dict
    flags: list[dict] = field(default_factory=list)  # {path, reason}
    repaired: bool = False


def _parse(text: str) -> tuple[dict | None, list[str]]:
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    try:
        v = json.loads(t)
    except ValueError as e:
        return None, [f"invalid JSON: {e}"]
    if not isinstance(v, dict):
        return None, ["top level must be a JSON object"]
    return v, []


def _norm(s: str) -> str:
    return " ".join(s.split())


def check_citations(result: dict, pages: list[str]) -> list[dict]:
    """Zero the confidence of any non-null field whose quote is not in its OCR page. Returns flags."""
    norm_pages = [_norm(p) for p in pages]
    flags: list[dict] = []

    def walk(node, path: str) -> None:
        if isinstance(node, list):
            for i, x in enumerate(node):
                walk(x, f"{path}[{i}]")
        elif isinstance(node, dict):
            src = node.get("source")
            if isinstance(src, dict) and "confidence" in node:
                if node.get("value") is not None:
                    page, quote = src.get("page"), _norm(str(src.get("quote", "")))
                    ok = (
                        isinstance(page, int)
                        and 1 <= page <= len(pages)
                        and quote
                        and quote in norm_pages[page - 1]
                    )
                    if not ok:
                        node["confidence"] = 0
                        flags.append({"path": path, "reason": "quote_not_in_ocr_text"})
                return
            for k, x in node.items():
                walk(x, f"{path}.{k}")

    walk(result, "$")
    return flags


def _mean_conf(node) -> float:
    vals: list[float] = []

    def walk(n) -> None:
        if isinstance(n, list):
            for x in n:
                walk(x)
        elif isinstance(n, dict):
            if isinstance(n.get("source"), dict) and "confidence" in n:
                if n.get("value") is not None:
                    vals.append(float(n["confidence"]))
                return
            for x in n.values():
                walk(x)

    walk(node)
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def classify_unit(pages: list[str], client: GatewayClient) -> tuple[str, float]:
    c = client.complete(classify_prompt(pages), max_output_tokens=100)
    d, errs = _parse(c.text)
    if errs or d.get("unit") not in UNITS:
        raise ExtractionError("unit classification failed")
    return d["unit"], c.cost_usd


def run_extraction(
    document_id: str, pages: list[str], client: GatewayClient, unit: str | None = None
) -> ExtractionRun:
    cost = 0.0
    if unit is None:
        unit, cost = classify_unit(pages, client)
    if unit not in UNITS:
        raise ExtractionError(f"unknown unit {unit!r}")
    schemas = load_schemas()
    validator = Validator(list(schemas.values()))
    schema = schemas[unit]

    errors: list[str] = []
    for attempt in (1, 2):  # one repair retry
        c = client.complete(extract_prompt(unit, schema, pages, errors or None))
        cost += c.cost_usd
        result, errors = _parse(c.text)
        if result is not None:
            errors = validator.errors(result, schema)
        if not errors:
            flags = check_citations(result, pages)
            return ExtractionRun(
                document_id,
                unit,
                c.model,
                PROMPT_VERSION,
                round(cost, 6),
                _mean_conf(result),
                result,
                flags,
                repaired=attempt == 2,
            )
    raise ExtractionError("output failed schema validation after repair: " + "; ".join(errors[:3]))
