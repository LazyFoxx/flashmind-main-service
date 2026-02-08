from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.core.settings.database import DatabaseSettings


def create_engine(settings: DatabaseSettings) -> AsyncEngine:
    return create_async_engine(
        url=str(settings.get_url()),
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        echo=settings.echo,
        pool_pre_ping=True,
        future=True,
    )
