from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities import CloudCardTemplate
from src.infrastructure.db.base import Base

if TYPE_CHECKING:
    from src.infrastructure.db.models.cloud_deck import CloudDeckModel


class CloudCardTemplateModel(Base):
    __tablename__ = "cloud_card_templates"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    cloud_deck_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("cloud_decks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    front: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    back: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    cloud_deck: Mapped["CloudDeckModel"] = relationship(
        "CloudDeckModel",
        back_populates="card_templates",
        lazy="raise",
    )

    def to_entity(self) -> CloudCardTemplate:
        return CloudCardTemplate(
            id=self.id,
            cloud_deck_id=self.cloud_deck_id,
            front=self.front,
            back=self.back,
        )

    @classmethod
    def from_domain(cls, template: CloudCardTemplate) -> "CloudCardTemplateModel":
        return CloudCardTemplateModel(
            id=template.id,
            cloud_deck_id=template.cloud_deck_id,
            front=template.front,
            back=template.back,
        )