from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.user.user import User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получить пользователя по его уникальному идентификатору.

        Args:
            user_id: UUID пользователя

        Returns:
            Объект User, если найден, иначе None
        """
        ...

    @abstractmethod
    async def add(self, user: User) -> None:
        """Добавить нового пользователя в хранилище.

        Пользователь должен быть новым (без ID или с временным).
        После добавления у пользователя должен появиться валидный ID из БД.

        Args:
            user: Объект User с валидными данными

        Raises:
            IntegrityError: если email уже занят
        """
        ...

    @abstractmethod
    async def update(self, user: User) -> None:
        """
        Обновляет существующего пользователя.

        Args:
            user: Объект User

        """
        ...
