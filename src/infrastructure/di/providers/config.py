from dishka import Provider, Scope, provide

from src.core.settings import (
    AuthSettings,
    DatabaseSettings,
    RabbitSettings,
    RedisSettings,
    S3Settings,
    AISettings
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

    @provide(scope=Scope.APP)
    def s3_settings(self) -> S3Settings:
        return S3Settings()

    @provide(scope=Scope.APP)
    def rabbit_settings(self) -> RabbitSettings:
        return RabbitSettings()
    
    @provide(scope=Scope.APP)
    def ai_settings(self) -> AISettings:
        return AISettings()
