"""Security middleware for OWASP compliance."""

import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.config import get_settings
from app.core.logging import get_logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add OWASP recommended security headers to all responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        settings = get_settings()
        response = await call_next(request)

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://*.supabase.co; "
            "frame-ancestors 'none';"
        )
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if "Server" in response.headers:
            del response.headers["Server"]

        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Generate and propagate request IDs for tracing."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log audit trail for sensitive operations."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.logger = get_logger("audit")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.monotonic()
        response = await call_next(request)
        duration_ms = int((time.monotonic() - start_time) * 1000)

        should_log = request.url.path.startswith("/api/v1/admin") or request.method in (
            "POST",
            "PATCH",
            "DELETE",
            "PUT",
        )

        if should_log:
            self.logger.info(
                "audit_log",
                request_id=getattr(request.state, "request_id", None),
                user_id=getattr(request.state, "user_id", None),
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                client_ip=request.client.host if request.client else None,
            )

        return response
