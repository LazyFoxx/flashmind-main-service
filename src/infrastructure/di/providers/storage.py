from dishka import Provider, Scope, provide
from src.infrastructure.storage.cloud_storage_service import YandexObjectStorage
from src.application.interfaces import AbstractCloudStorage
from src.core.settings.s3 import S3Settings


class StorageProvider(Provider):
    @provide(scope=Scope.APP)
    def cloud_storage(self, settings: S3Settings) -> AbstractCloudStorage:
        return YandexObjectStorage(settings)


