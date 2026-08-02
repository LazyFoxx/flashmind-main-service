from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities import CloudDeck
from src.infrastructure.db.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models.cloud_card import CloudCardTemplateModel


class CloudDeckModel(Base):
     __tablename__ = "cloud_decks"

     id: Mapped[UUID] = mapped_column(
         PG_UUID(as_uuid=True),
         primary_key=True,
      )

     author_id: Mapped[UUID] = mapped_column(
         PG_UUID(as_uuid=True),
         ForeignKey("user_profiles.id", ondelete="CASCADE"),
         nullable=False,
         index=True,
      )

     name: Mapped[str] = mapped_column(
         String(120),
         nullable=False,
         index=True,
      )

     description: Mapped[Optional[str]] = mapped_column(
         Text,
         nullable=True,
      )

     type: Mapped[str] = mapped_column(
         String(10),
         nullable=False,
         server_default="'PRIVATE'",
         index=True,
      )

     is_approved: Mapped[bool] = mapped_column(
         Boolean,
         nullable=False,
         default=False,
         server_default="false",
         index=True,
      )

     approved_at: Mapped[Optional[datetime]] = mapped_column(
         DateTime(timezone=True),
         nullable=True,
      )

     created_at: Mapped[datetime] = mapped_column(
         server_default=func.now(),
         nullable=False,
      )

     updated_at: Mapped[datetime] = mapped_column(
         server_default=func.now(),
         onupdate=func.now(),
         nullable=False,
      )
     
     last_synced_at: Mapped[Optional[datetime]] = mapped_column(
         server_default=func.now(),
         nullable=True,
        )
     
     downloaded: Mapped[int] = mapped_column(
         Integer,
         nullable=False,
         default=0,
         server_default="0",
         comment="Количество скачиваний колоды другими пользователями",
      )
     

     # Relationships
     card_templates: Mapped[list["CloudCardTemplateModel"]] = relationship(
          "CloudCardTemplateModel",
         back_populates="cloud_deck",
         cascade="all, delete-orphan",
         lazy="selectin",
      )
     
     previous_authors: Mapped[list[UUID]] = mapped_column(
         ARRAY(PG_UUID(as_uuid=True)),
         nullable=False,
         server_default="{}",
      )

     def to_entity(self) -> CloudDeck:
         return CloudDeck(
             id=self.id,
             author_id=self.author_id,
             name=self.name,
             description=self.description or "",
             type=self.type,
             is_approved=self.is_approved,
             approved_at=self.approved_at,
             downloaded=self.downloaded,
             last_synced_at=self.last_synced_at,
             previous_authors=self.previous_authors or [],
          )

     @classmethod
     def from_domain(cls, deck: CloudDeck) -> "CloudDeckModel":
         return CloudDeckModel(
             id=deck.id,
             author_id=deck.author_id,
             name=deck.name,
             description=deck.description,
             type=deck.type,
             is_approved=deck.is_approved,
             approved_at=deck.approved_at,
             downloaded=deck.downloaded,
             last_synced_at=getattr(deck, "last_synced_at", None),
             previous_authors=deck.previous_authors,
          )
