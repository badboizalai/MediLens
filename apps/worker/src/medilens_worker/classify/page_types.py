"""Page types (D54: "9 page types").

The plan (project-plan §25.1) fixes the count (9) but not the names. The names come from the
page-classification prompt in `.claude/skills/medilens-ai-ml-engineer/references/prompt-library.md`
(`doc_type` enum). `UNKNOWN` is not a 10th type: it is the "no rule fired" sentinel.
"""

from __future__ import annotations

from enum import Enum
from typing import Protocol


class PageType(str, Enum):
    DISCHARGE_SUMMARY = "discharge_summary"
    OUTPATIENT_FORM = "outpatient_form"
    LAB_RESULT = "lab_result"
    PATHOLOGY_REPORT = "pathology_report"
    IMAGING_REPORT = "imaging_report"
    DENTAL_RECORD = "dental_record"
    PRESCRIPTION = "prescription"
    ORDER_FORM = "order_form"
    OTHER = "other"
    UNKNOWN = "unknown"  # sentinel: rules did not fire; caller may fall back to the LLM


class LlmClassifier(Protocol):
    """Tier-S zero-shot fallback for low-confidence rule results. Interface only (no gateway yet)."""

    def classify(self, text: str) -> tuple[PageType, float]: ...
