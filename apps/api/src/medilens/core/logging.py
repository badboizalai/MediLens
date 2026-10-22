"""structlog JSON logging with a PHI-safe processor."""

import logging
from typing import Any

import structlog

# Keys that may carry PHI/PII/secrets; values are never logged.
SENSITIVE_KEYS = frozenset(
    {
        "name",
        "full_name",
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "dob",
        "date_of_birth",
        "national_id",
        "cccd",
        "ssn",
        "diagnosis",
        "icd10",
        "medication",
        "finding",
        "findings",
        "text",
        "ocr_text",
        "raw_text",
        "prompt",
        "body",
        "password",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "cookie",
        "secret",
        "api_key",
    }
)
REDACTED = "[REDACTED]"


def _scrub(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: REDACTED if str(k).lower() in SENSITIVE_KEYS else _scrub(v) for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_scrub(v) for v in value]
    return value


def drop_phi(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    return _scrub(event_dict)


def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
    renderer = structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            drop_phi,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
