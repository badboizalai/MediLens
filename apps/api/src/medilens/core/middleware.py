"""Pure ASGI middleware: request id (X-Request-ID) and security headers."""

import re
import uuid

import structlog
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

HEADER = "X-Request-ID"
_VALID = re.compile(r"^[A-Za-z0-9._-]{8,128}$")  # reject anything that could forge log lines


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(HEADER.lower().encode(), b"").decode("latin-1")
        rid = incoming if _VALID.match(incoming) else uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = rid
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=rid)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)[HEADER] = rid
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            structlog.contextvars.clear_contextvars()


_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
}
_API_CSP = "default-src 'none'; frame-ancestors 'none'"
_DOCS_PREFIXES = ("/docs", "/openapi.json")  # Swagger UI needs scripts; docs are off in prod


class SecurityHeadersMiddleware:
    """JSON API: lock down framing/sniffing and forbid caching (responses may carry PHI)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        is_docs = scope["path"].startswith(_DOCS_PREFIXES)

        async def send_secure(message: Message) -> None:
            if message["type"] == "http.response.start":
                h = MutableHeaders(scope=message)
                for k, v in _SECURITY_HEADERS.items():
                    h[k] = v
                if not is_docs:
                    h["Content-Security-Policy"] = _API_CSP
                if "cache-control" not in h:
                    h["Cache-Control"] = "no-store"
            await send(message)

        await self.app(scope, receive, send_secure)
