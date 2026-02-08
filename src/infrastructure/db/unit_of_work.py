from types import TracebackType
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import AbstractUnitOfWork
from src.infrastructure.db.repositories import SQlAlchemyUserRepository


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        # Репозитории создаём здесь — они используют текущую session
        self.users = SQlAlchemyUserRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        # Если исключения не было — сессия закоммитится в use case (явно)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
