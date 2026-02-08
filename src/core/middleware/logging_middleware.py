import json
import time
import uuid
from contextvars import Token
from typing import Any, Awaitable, Callable, Dict

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging.config import request_id_var

SENSITIVE_FIELDS = {
    "password",
    "token",
    "secret",
    "authorization",
    "api_key",
    "cookie",
    "x-api-key",
    "bearer",
}


def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Маскирует/убирает headers. Укажи, что убрать/маскировать."""
    sanitized = headers.copy()  # Не мутировать оригинал

    # Маскируем sensitive
    mask_keys = ["authorization", "cookie", "x-auth-token"]
    for key in mask_keys:
        if key in sanitized:
            sanitized[key] = "******"

    # Убираем шумные/ненужные
    remove_keys = [
        "user-agent",
        "accept-encoding",
        "accept-language",
        "referer",
        "connection",
        "content-length",
    ]
    for key in remove_keys:
        sanitized.pop(key, None)

    return sanitized


def mask_sensitive(data: Dict[str, Any]) -> Dict[str, Any]:
    """Маскирует sensitive поля в dict (body или headers)."""
    masked = {}
    for k, v in data.items():
        key_lower = k.lower()
        if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
            masked[k] = "******"
        else:
            masked[k] = v
    return masked


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = str(uuid.uuid4())[:8]
        token: Token[str] = request_id_var.set(request_id)
        logger = structlog.get_logger("http")
        start_time = time.perf_counter()

        # Body (если есть)
        body: Dict[str, Any] = {}
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                body = json.loads(body_bytes) if body_bytes else {}
                body = mask_sensitive(body)
            except json.JSONDecodeError:
                body = {"error": "Invalid JSON"}

        # Headers с маской
        headers = sanitize_headers(dict(request.headers))

        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            body=body,
            headers=headers,
        )

        try:
            response: Response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
        except Exception as exc:
            logger.error("Request failed", exc_info=exc)
            raise
        finally:
            request_id_var.reset(token)

        return response
