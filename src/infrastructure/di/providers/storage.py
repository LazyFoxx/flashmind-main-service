from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from src.infrastructure.storage.storage_cache_redis import RedisS3Cache
from src.application.interfaces import AbstractS3Cache
from src.infrastructure.storage.cloud_storage_service import YandexObjectStorage
from src.application.interfaces import AbstractCloudStorage
from src.core.settings.s3 import S3Settings


class StorageProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_s3_cache(self, redis: Redis) -> AbstractS3Cache:
        return RedisS3Cache(redis)

    @provide(scope=Scope.APP)
    def cloud_storage(self, settings: S3Settings, cache: AbstractS3Cache) -> AbstractCloudStorage:
        return YandexObjectStorage(settings, cache)
    

