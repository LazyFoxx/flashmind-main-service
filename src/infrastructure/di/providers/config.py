from dishka import Provider, Scope, provide

from src.core.settings import (
    AuthSettings,
    DatabaseSettings,
    RedisSettings,
)


class ConfigProvider(Provider):
    # Целые объекты настроек
    @provide(scope=Scope.APP)
    @provide(scope=Scope.APP)
    def db_settings(self) -> DatabaseSettings:
        return DatabaseSettings()

    @provide(scope=Scope.APP)
    def redis_settings(self) -> RedisSettings:
        return RedisSettings()

    @provide(scope=Scope.APP)
    def auth_settings(self) -> AuthSettings:
        return AuthSettings()
