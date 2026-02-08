from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.logging.config import setup_logging
from src.core.middleware.logging_middleware import LoggingMiddleware
from src.core.settings import cors_config
from src.infrastructure.di.container import get_container
from src.presentation.api.exception_handlers import setup_exception_handlers
from src.presentation.api.routers.root import api_router

container = get_container()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    setup_logging()
    yield
    # shutdown
    await container.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.origins,
    allow_origin_regex=cors_config.origin_regex,
    allow_credentials=cors_config.allow_credentials,
    allow_methods=cors_config.allow_methods,
    allow_headers=cors_config.allow_headers,
)

setup_dishka(container, app=app)
setup_exception_handlers(app)


app.include_router(api_router)
