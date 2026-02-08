from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import AbstractUserRepository, User
from src.infrastructure.db.models import UserProfileModel


class SQlAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserProfileModel).where(UserProfileModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_entity() if user_model else None

    async def add(self, user: User) -> None:
        user_model = UserProfileModel.from_domain(user)
        self.session.add(user_model)

    async def update(self, user: User) -> None:
        # Обычно делаем через merge или update-выражение
        stmt = (
            update(UserProfileModel)
            .where(UserProfileModel.id == user.id)
            .values(
                first_name=user.first_name,
                last_name=user.last_name,
                avatar_url=user.avatar_url,
                bio=user.bio,
            )
        )
        await self.session.execute(stmt)
