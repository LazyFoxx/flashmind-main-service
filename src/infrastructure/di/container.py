from dishka import AsyncContainer, make_async_container

from .providers import (
    AuthProvider,
    ConfigProvider,
    DbProvider,
    RedisProvider,
    UseCaseProvider,
)

# Список всех провайдеров
_PROVIDERS = [
    ConfigProvider(),
    DbProvider(),
    RedisProvider(),
    UseCaseProvider(),
    AuthProvider(),
]


def get_container() -> AsyncContainer:
    """
    Фабрика для создания Dishka контейнера.
    Вызывается только при старте приложения (в lifespan) или в тестах.
    """
    return make_async_container(*_PROVIDERS)
