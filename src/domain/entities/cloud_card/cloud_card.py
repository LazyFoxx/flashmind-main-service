from dataclasses import dataclass, replace
from uuid import UUID
from datetime import datetime, timezone


@dataclass(slots=True, frozen=True)
class CloudCardTemplate:
    """Шаблон карточки внутри облачной колоды."""
    id: UUID
    cloud_deck_id: UUID
    front: str
    back: str
    
    def set_front_and_back(self, front: str, back: str) -> "CloudCardTemplate":
        """устанавливает card template id."""
        return replace(self, front=front, back=back)