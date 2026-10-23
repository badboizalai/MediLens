"""Projection of a confirmed extraction into clinical facts. Pure: no framework types.

Rules: the user's edit wins over the model value; no region_code means a condition without a
body finding (never guess); is_metastasis only for metastases[] entries not stated as suspected;
no ICD-10 codes are written (LIC-002).
"""

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Protocol
from uuid import UUID

from medilens.core.errors import NotFound

_REGION = re.compile(r"^[a-z][a-z0-9_]*$")
_LOINC = re.compile(r"^\d{1,7}-\d$")
_RANGE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*[-–]\s*(-?\d+(?:\.\d+)?)\s*$")
_TOKEN = re.compile(r"[^.\[\]]+|\[\d+\]")


# shortcut: minimal copy of the ai-gateway guardrails emergency list (BR-041); apps share no code,
# move to a shared package when a third consumer needs it. Matched on diacritic-free text.
EMERGENCY = re.compile(
    r"dau nguc|kho tho|khong tho duoc|ngat xiu|bat tinh|co giat|dot quy|meo mieng|"
    r"yeu (nua nguoi|liet)|chay mau (nhieu|khong cam)|(non|ho) ra mau|"
    r"chest (pain|tightness)|short(ness)? of breath|(can ?not|can't|cant|trouble|difficulty) breath|"
    r"heart attack|severe bleeding|unconscious|seizure|having a stroke"
)


def norm(text: str) -> str:
    """Lowercase, strip diacritics (incl. d-stroke), collapse whitespace."""
    t = unicodedata.normalize("NFKD", text.replace("đ", "d").replace("Đ", "D").lower())
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c))).strip()


@dataclass(frozen=True)
class ReportResult:
    emergency: bool
    condition_id: UUID | None = None
    region_code: str | None = None
    laterality: str | None = None


class ProfileNotFound(NotFound):
    """Also used for other users' profiles: existence is never leaked."""

    def __init__(self) -> None:
        super().__init__("Resource not found.")


@dataclass(frozen=True)
class Finding:
    region_code: str
    laterality: str | None
    size_mm: float | None
    is_metastasis: bool


@dataclass(frozen=True)
class ConditionDraft:
    label: str
    unit_code: str
    severity: str | None = None
    status: str | None = None
    stage: str | None = None
    finding: Finding | None = None


@dataclass(frozen=True)
class ObservationDraft:
    name: str
    value: str | None
    unit: str | None
    loinc_code: str | None
    ref_low: float | None
    ref_high: float | None


@dataclass(frozen=True)
class Projection:
    unit_code: str
    encounter_date: date | None
    facility: str | None
    department: str | None
    conditions: list[ConditionDraft] = field(default_factory=list)
    observations: list[ObservationDraft] = field(default_factory=list)


@dataclass(frozen=True)
class FindingView:
    id: UUID
    region_code: str
    laterality: str | None
    severity: str | None
    unit_code: str | None
    is_metastasis: bool
    observed_at: datetime | None
    document_id: UUID | None
    label: str | None
    source: str


@dataclass(frozen=True)
class ObservationView:
    id: UUID
    name: str
    value: str | None
    unit: str | None
    loinc_code: str | None
    ref_low: float | None
    ref_high: float | None
    observed_at: datetime | None
    document_id: UUID | None


class ClinicalRepository(Protocol):
    def resolve(self, subject: str) -> UUID | None:
        """The caller's user id; binds the transaction's RLS scope to their profiles."""

    def owns(self, user_id: UUID, profile_id: UUID) -> bool: ...

    def load_run(self, run_id: UUID) -> tuple[UUID, dict[str, Any], dict[str, str]] | None:
        """(profile_id, raw_output, {field_path: user_value})."""

    def add_reported(
        self,
        profile_id: UUID,
        label: str,
        region_code: str | None,
        laterality: str | None,
        observed_at: datetime | None,
    ) -> UUID: ...

    def replace(self, run_id: UUID, profile_id: UUID, projection: Projection) -> None: ...
    def findings(self, profile_id: UUID, after: UUID | None, limit: int) -> list[FindingView]: ...
    def observations(self, profile_id: UUID, limit: int) -> list[ObservationView]: ...


def _set(root: Any, path: str, value: str) -> None:
    node = root
    try:
        for t in _TOKEN.findall(path):
            node = node[int(t[1:-1])] if t[0] == "[" else node[t]
        if isinstance(node, dict) and "source" in node:
            node["value"] = value
    except (KeyError, IndexError, TypeError):
        pass  # stale path: ignore rather than fail the confirm


def _val(node: Any) -> Any:
    return node.get("value") if isinstance(node, dict) else None


def _num(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _str(v: Any) -> str | None:
    return None if v is None or str(v).strip() == "" else str(v).strip()


def _date(v: Any) -> date | None:
    try:
        return date.fromisoformat(v)
    except (TypeError, ValueError):
        return None


def _finding(
    item: dict[str, Any], laterality: str | None, size: float | None, meta: bool
) -> Finding | None:
    code = (item.get("region") or {}).get("region_code")
    if isinstance(code, str) and _REGION.match(code):
        return Finding(code, laterality, size, meta)
    return None  # unmapped: kept as a condition only


def project(raw: dict[str, Any], overrides: dict[str, str]) -> Projection | None:
    """None when the result is not a known Unit. `raw` is mutated: pass a copy."""
    for path, v in overrides.items():
        _set(raw, path, v)
    enc = raw.get("encounter") or {}
    conds: list[ConditionDraft] = []
    obs: list[ObservationDraft] = []
    if "teeth" in raw:
        unit = "dental"
        for t in raw["teeth"]:
            fdi, kind = _str(_val(t.get("fdi"))), t.get("condition")
            if fdi and kind:
                conds.append(
                    ConditionDraft(
                        f"{kind} (FDI {fdi})",
                        unit,
                        severity=t.get("severity"),
                        finding=_finding(t, None, None, False),
                    )
                )
    elif "diagnoses" in raw:
        unit = "cardiology"
        for d in raw["diagnoses"]:
            text = _str(_val(d.get("text")))
            if text:
                lat = d.get("laterality")
                conds.append(
                    ConditionDraft(
                        text,
                        unit,
                        severity=d.get("severity"),
                        finding=_finding(d, lat, None, False),
                    )
                )
        for o in raw.get("observations", []):
            name = _str(_val(o.get("name")))
            if not name:
                continue
            rng = _RANGE.match(_str(_val(o.get("reference_range"))) or "")
            loinc = o.get("loinc_hint")
            obs.append(
                ObservationDraft(
                    name,
                    _str(_val(o.get("value"))),
                    _str((o.get("value") or {}).get("unit")),
                    loinc if isinstance(loinc, str) and _LOINC.match(loinc) else None,
                    float(rng[1]) if rng else None,
                    float(rng[2]) if rng else None,
                )
            )
    elif "primary" in raw:
        unit = "oncology"
        p = raw["primary"]
        label = _str(_val(p.get("histology"))) or _str(_val(p.get("site")))
        if label:
            conds.append(
                ConditionDraft(
                    label,
                    unit,
                    stage=_str(_val((raw.get("tnm") or {}).get("stage"))),
                    finding=_finding(p, p.get("laterality"), _num(_val(p.get("size_mm"))), False),
                )
            )
        for m in raw.get("metastases", []):
            site = _str(_val(m.get("site")))
            if site:
                stated = m.get("stated_as")
                conds.append(
                    ConditionDraft(
                        f"metastasis: {site}",
                        unit,
                        status=stated,
                        finding=_finding(m, None, None, stated != "suspected"),
                    )
                )
    else:
        return None
    return Projection(
        unit,
        _date(_val(enc.get("date"))),
        _str(_val(enc.get("facility"))),
        _str(_val(enc.get("department"))),
        conds,
        obs,
    )
