import logging
import os
import sys
from contextvars import ContextVar
from typing import Any

import structlog

request_id_var: ContextVar[str] = ContextVar("request_id", default="no_request")


def get_request_id() -> str:
    return request_id_var.get()


class RequestIDProcessor:
    def __call__(
        self,
        logger: Any,
        method_name: str,
        event_dict: dict[str, Any],
    ) -> dict[str, Any]:
        event_dict["request_id"] = get_request_id()
        return event_dict


def setup_logging() -> None:
    env = os.getenv("ENV", "dev").lower()
    is_prod = env == "prod"

    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        RequestIDProcessor(),
    ]

    if is_prod:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if not is_prod else logging.INFO)

    if is_prod:
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_log_level,
            ],
        )
        handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if not is_prod else logging.INFO)

    noisy = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "sqlalchemy",
        "httpx",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
    ]
    for name in noisy:
        logger = logging.getLogger(name)
        logger.setLevel(logging.WARNING)
        logger.handlers = [handler]
        logger.propagate = False

    structlog.get_logger("setup").info(
        "Logging configured", environment=env, mode="json" if is_prod else "pretty"
    )
