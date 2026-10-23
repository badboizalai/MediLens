"""Extraction orchestration: classify -> extract -> validate (+1 repair) -> cite-check."""

import json
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Protocol
from urllib import request as urlrequest

import structlog
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from medilens_worker.anatomy.mapper import map_region
from medilens_worker.classify.page_types import PageType
from medilens_worker.classify.rules import LLM_FALLBACK_THRESHOLD, classify_text

from .prompts import PROMPT_VERSION, UNITS, classify_prompt, extract_prompt, load_schemas
from .service_token import mint

GATEWAY_AUDIENCE = "ai-gateway"  # apps/ai-gateway main.py AUDIENCE
PIPELINE_VERSION = "worker-extract-1"  # bump when pipeline behaviour changes


log = structlog.get_logger()

# Page type -> Unit. Types absent here (labs, prescriptions, ...) carry no Unit signal.
PAGE_TYPE_UNIT = {PageType.DENTAL_RECORD: "dental", PageType.PATHOLOGY_REPORT: "oncology"}


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
        self,
        base_url: str,
        tenant_id: str,
        secret: str,
        profile_id: str = "extract",
        timeout: float = 60,
    ) -> None:
        self._url = base_url.rstrip("/") + "/v1/complete"
        self._secret = secret
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
        token = mint(  # fresh single-use token per request; scope pinned to our tenant/profile
            self._secret,
            caller="worker",
            audience=GATEWAY_AUDIENCE,
            tenants=[self._tenant],
            profiles=[self._profile],
        )
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        req = urlrequest.Request(self._url, body, headers)  # noqa: S310 - fixed internal URL
        with urlrequest.urlopen(req, timeout=self._timeout) as r:  # noqa: S310 - fixed internal URL
            d = json.load(r)
        return Completion(d["text"], d["model"], float(d["cost_usd"]))


def uuid7() -> str:
    """RFC 9562 uuid7 (48-bit ms timestamp first, so ids sort by creation time). stdlib has it only from 3.14."""
    b = bytearray(os.urandom(16))
    b[:6] = (time.time_ns() // 1_000_000).to_bytes(6, "big")
    b[6] = 0x70 | (b[6] & 0x0F)
    b[8] = 0x80 | (b[8] & 0x3F)
    return str(uuid.UUID(bytes=bytes(b)))


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
    run_id: str = field(default_factory=uuid7)  # one per extraction run
    pipeline_version: str = PIPELINE_VERSION


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


def _locations(result: dict, unit: str):
    """(path, holder, location StringField) for every item that gets a `region`."""
    if unit == "dental":
        for i, t in enumerate(result.get("teeth", [])):
            yield f"$.teeth[{i}]", t, t.get("fdi")
    elif unit == "cardiology":
        for i, d in enumerate(result.get("diagnoses", [])):
            yield f"$.diagnoses[{i}]", d, d.get("site")
    elif unit == "oncology":
        if isinstance(result.get("primary"), dict):
            yield "$.primary", result["primary"], result["primary"].get("site")
        for i, m in enumerate(result.get("metastases", [])):
            yield f"$.metastases[{i}]", m, m.get("site")


def map_regions(result: dict, unit: str) -> list[dict]:
    """Set `region` {region_code, confidence} on each located item; region_code null = unmapped.
    Unmapped items are kept and flagged, never dropped (illustration only, BR-042)."""
    flags: list[dict] = []
    for path, item, loc in _locations(result, unit):
        text = loc.get("value") if isinstance(loc, dict) else None
        code, conf = map_region(text, unit) if isinstance(text, str) else (None, 0.0)
        item["region"] = {"region_code": code, "confidence": conf}
        if code is None:
            flags.append({"path": f"{path}.region", "reason": "region_unmapped"})
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


def unit_from_pages(pages: list[str]) -> str | None:
    """Unit from the rules classifier; None (=> LLM classify) unless the confident, mapped pages
    all agree on one Unit (unmapped/low-confidence pages are ignored). Never guesses."""
    units = set()
    for text in pages:
        page_type, conf = classify_text(text)
        if conf >= LLM_FALLBACK_THRESHOLD and page_type in PAGE_TYPE_UNIT:
            units.add(PAGE_TYPE_UNIT[page_type])
    unit = units.pop() if len(units) == 1 else None
    log.info("rules_unit", unit=unit, pages=len(pages))  # labels only, never page text
    return unit


def run_extraction(
    document_id: str, pages: list[str], client: GatewayClient, unit: str | None = None
) -> ExtractionRun:
    cost = 0.0
    if unit is None:
        unit = unit_from_pages(pages)
    if unit is None:
        unit, cost = classify_unit(pages, client)
    if unit not in UNITS:
        raise ExtractionError(f"unknown unit {unit!r}")
    schemas = load_schemas()
    registry = Registry().with_resources(
        [(s["$id"], Resource.from_contents(s)) for s in schemas.values()]
    )
    validator = Draft202012Validator(schemas[unit], registry=registry)
    schema = schemas[unit]

    errors: list[str] = []
    for attempt in (1, 2):  # one repair retry
        c = client.complete(extract_prompt(unit, schema, pages, errors or None))
        cost += c.cost_usd
        result, errors = _parse(c.text)
        if result is not None:
            errors = [
                f"{e.json_path}: {e.message}"[:300]
                for e in sorted(validator.iter_errors(result), key=lambda e: e.json_path)
            ]
        if not errors:
            flags = check_citations(result, pages) + map_regions(result, unit)
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
