from abc import ABC, abstractmethod
from typing import Any, Mapping
from uuid import UUID

from fastapi import UploadFile


class AbstractCloudStorage(ABC):
    @abstractmethod
    async def put_avatar(self, user_id: str, category: str, file: UploadFile) -> str:
        """Загружает фотографию в облачное хранилище и возвращет object_key.

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
    
    @abstractmethod
    async def delete_object(self, object_key: str, user_id: UUID) -> bool:
        """Удаляет объект из облачного хранилища по ключу.

        Args:
            object_key: ключ объекта (например, "avatars/user123/avatar.jpg")

        Returns:
            bool: True — если объект успешно удалён, False — если объект не найден
                  или произошла ошибка при удалении
        """
        raise NotImplementedError
    
    