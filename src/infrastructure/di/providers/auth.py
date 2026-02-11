from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from src.application.interfaces import AbstractJWKSCache
from src.infrastructure.auth.auth_service import AuthService
from src.infrastructure.auth.jwks_cache_redis import RedisJWKSCache
from src.infrastructure.auth.jwks_client import JWKSClient


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_jwks_cache(self, redis: Redis) -> AbstractJWKSCache:
        return RedisJWKSCache(redis)

    jwks_client = provide(JWKSClient, scope=Scope.APP)
    auth_service = provide(AuthService, scope=Scope.APP)
