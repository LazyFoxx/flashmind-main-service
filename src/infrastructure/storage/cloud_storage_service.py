import aioboto3
import uuid
from datetime import datetime
from PIL import Image
import io
from asyncio import to_thread
from fastapi import HTTPException, UploadFile
from src.application.interfaces import AbstractCloudStorage
from src.core.settings import S3Settings
from botocore.config import Config

class YandexObjectStorage(AbstractCloudStorage):
    def __init__(self, settings: S3Settings):
        self.settings = settings
        self.botocore_config = Config(
            signature_version="s3v4",
            retries={'max_attempts': 3, 'mode': 'standard'},
            connect_timeout=5,
            read_timeout=15,
        )
        self.session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.region_name,
        )

    def _optimize_avatar_to_webp(self,
        content: bytes,
        max_size: tuple = (512, 512),          
        quality: int = 80,                     # 75–85 — оптимально
    ) -> tuple[bytes, str]:
        """
        Синхронная функция — принимает уже прочитанные байты

        Возвращает: (webp-байты, 'image/webp')
        """
        try:
            img = Image.open(io.BytesIO(content))
            img = img.convert("RGB")           # убираем альфу
        except Exception:
            raise HTTPException(400, "Невалидное изображение")

        # Ресайз с сохранением пропорций
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()

        # Сохраняем как WebP (lossy)
        img.save(
            output,
            format="WEBP",
            quality=quality,
            method=6,                          # 4–6 = максимальная компрессия
            lossless=False,
        )

        webp_bytes = output.getvalue()

        return webp_bytes, "image/webp"


    async def put_avatar(self, user_id: str, category: str, file: UploadFile) -> str:
        
        content = await file.read()
        webp_content, content_type = await to_thread(self._optimize_avatar_to_webp,
        content)

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
                CacheControl="public, max-age=2592000"
            )

        return object_key

    async def generate_presigned_url(self, object_key: str, expires_in: int) -> str:


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
            HttpMethod="GET"
        )
        return url
