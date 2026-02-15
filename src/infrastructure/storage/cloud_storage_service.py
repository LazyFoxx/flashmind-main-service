import io
import uuid
from asyncio import to_thread
from datetime import datetime

import aioboto3
import structlog
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile
from PIL import Image

from src.application.interfaces import AbstractCloudStorage, AbstractS3Cache
from src.core.settings import S3Settings


class YandexObjectStorage(AbstractCloudStorage):
    def __init__(self, settings: S3Settings, cache: AbstractS3Cache):
        self.settings = settings
        self.cache = cache
        self.botocore_config = Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=5,
            read_timeout=15,
        )
        self.session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.region_name,
        )
        self.logger = structlog.get_logger(__name__)

    def _optimize_avatar_to_webp(
        self,
        content: bytes,
        max_size: tuple[int, int] = (512, 512),
        quality: int = 80,  # 75–85 — оптимально
    ) -> tuple[bytes, str]:
        """
        Синхронная функция — принимает уже прочитанные байты

        Возвращает: (webp-байты, 'image/webp')
        """
        try:
            img = Image.open(io.BytesIO(content))
            img = img.convert("RGB")  # убираем альфу
        except Exception as e:
            raise HTTPException(400, "Невалидное изображение") from e

        # Ресайз с сохранением пропорций
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()

        # Сохраняем как WebP (lossy)
        img.save(
            output,
            format="WEBP",
            quality=quality,
            method=6,  # 4–6 = максимальная компрессия
            lossless=False,
        )

        webp_bytes = output.getvalue()

        return webp_bytes, "image/webp"

    async def put_avatar(self, user_id: str, category: str, file: UploadFile) -> str:
        content = await file.read()
        webp_content, content_type = await to_thread(
            self._optimize_avatar_to_webp, content
        )

        date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
        unique_part = str(uuid.uuid4())[:8]
        object_key = f"users/{user_id}/{category}/{date_prefix}-{unique_part}.webp"

        async with self.session.client(
            "s3",
            endpoint_url=self.settings.endpoint_url,
            config=self.botocore_config,
        ) as client:
            await client.put_object(
                Bucket=self.settings.bucket_name,
                Key=object_key,
                Body=webp_content,
                ContentType=content_type,
                CacheControl="public, max-age=2592000",
            )

            self.logger.info("Добавлена фотография в S3", user_id=str(user_id)[:8])

        return object_key

    async def generate_presigned_url(self, object_key: str, expires_in: int) -> str:
        # сначала проверяем на наличие в кеш
        url = await self.cache.get_url(key=object_key)
        if url:
            return url

        # генерируем новую ссылку
        async with self.session.client(
            "s3",
            endpoint_url=self.settings.endpoint_url,
            config=self.botocore_config,
        ) as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.settings.bucket_name,
                    "Key": object_key,
                },
                ExpiresIn=expires_in,
                HttpMethod="GET",
            )
        # сохраняем в кэш
        await self.cache.set_url(key=object_key, url=url, ttl=expires_in - 10)
        return str(url)

    async def delete_object(self, object_key: str, user_id: uuid.UUID) -> bool:
        async with self.session.client(
            "s3",
            endpoint_url=self.settings.endpoint_url,
            config=self.botocore_config,
        ) as client:
            try:
                await client.delete_object(
                    Bucket=self.settings.bucket_name,
                    Key=object_key,
                )
                self.logger.info(
                    "Обьект успешно удален в хранилище с ключем ", object_key=object_key
                )
                return True
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    return True  # Объект не существовал — считаем успешным (идемпотентность)
                # Логируем другие ошибки, если нужно (в проде добавь logger)
                self.logger.warning(
                    "Обьект не найден в S3 при удалении ", user_id=str(user_id)[:8]
                )
                return False
            except Exception as e:
                # Общая ошибка
                self.logger.error(
                    "Ошибка удаления обьекта из S3 ", user_id=str(user_id)[:8]
                )
                raise HTTPException(500, f"Ошибка удаления объекта: {str(e)}") from e
