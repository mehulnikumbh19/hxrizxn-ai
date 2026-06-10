from __future__ import annotations

import re
from collections import defaultdict
from time import monotonic

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


PROMPT_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"ignore\s+previous\s+instructions",
        r"developer\s+message",
        r"system\s+prompt",
        r"exfiltrate",
        r"reveal\s+hidden",
    ]
]

ALLOWED_UPLOAD_TYPES = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def redact_sensitive_text(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[redacted-email]", text)
    text = re.sub(r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b", "[redacted-ssn]", text)
    text = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "[redacted-card]", text)
    return text


def sanitize_retrieved_text(text: str) -> str:
    clean = redact_sensitive_text(text)
    for pattern in PROMPT_INJECTION_PATTERNS:
        clean = pattern.sub("[removed-instruction-like-text]", clean)
    return clean


def validate_upload_type(mime_type: str) -> None:
    if mime_type not in ALLOWED_UPLOAD_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {mime_type}")


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 180, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        client = request.client.host if request.client else "unknown"
        now = monotonic()
        bucket = [ts for ts in self._requests[client] if now - ts < self.window_seconds]
        bucket.append(now)
        self._requests[client] = bucket
        if len(bucket) > self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        return await call_next(request)

