from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional

from src.domain.entities import AbstractUserRepository


class AbstractUnitOfWork(ABC):
    """Минималистичный современный UoW для async"""

    users: AbstractUserRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Метод для обработки выхода из контекста"""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Коммит изменений"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Откат изменений"""
        pass
