from dataclasses import dataclass, replace
from typing import Any, Optional
from uuid import UUID
from datetime import datetime, timezone


@dataclass(slots=True, frozen=True)
class CloudCardTemplate:
    """Шаблон карточки внутри облачной колоды."""
    id: UUID
    cloud_deck_id: UUID
    title: str
    front: str
    back: str
    hint1: Optional[str] = None
    hint2: Optional[str] = None
    
    def set_content(
        self,
        front: Any,
        back: Any,
        title: Optional[str] = None,
        hint1: Optional[str] = None,
        hint2: Optional[str] = None,
    ) -> "CloudCardTemplate":
        """Обновляет содержимое шаблона (front/back/title/hint1/hint2)."""
        return replace(
            self,
            front=front,
            back=back,
            title=title if title is not None else self.title,
            hint1=hint1 if hint1 is not None else self.hint1,
            hint2=hint2 if hint2 is not None else self.hint2,
        )