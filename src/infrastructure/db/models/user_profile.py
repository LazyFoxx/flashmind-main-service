from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities import User
from src.infrastructure.db.base import Base


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    avatar_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    def to_entity(self) -> User:
        """Конвертирует загруженную ORM-модель в чистую доменную сущность."""
        return User(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            avatar_url=self.avatar_url,
            bio=self.bio,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserProfileModel":
        """Альтернативный конструктор: создаёт модель из доменной сущности."""
        return UserProfileModel(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
        )
