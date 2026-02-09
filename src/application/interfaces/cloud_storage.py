from abc import ABC, abstractmethod
from typing import Any, Mapping

from fastapi import UploadFile


class AbstractCloudStorage(ABC):
    @abstractmethod
    async def put_avatar(self, user_id: str, category: str, file: UploadFile) -> str:
        """Загружает фотографию в облачное хранилище и возвращет object_key."""
        """
        Args:
            user_id: идентификатор пользователя
            category: avatar,
            file: файл

        Returns:
            object_key: str
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_presigned_url(object_key: str, expires_in: int) -> str:
        """Получение временной ссылки для просмотра.

        Args:
            object_key: ключ обьекта в хранилище
            expires_in: доступ по ссылке в секундах

        Returns:
            view_url: str
        """
        raise NotImplementedError