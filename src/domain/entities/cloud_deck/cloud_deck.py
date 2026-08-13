from dataclasses import dataclass, field, replace
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

@dataclass(slots=True, frozen=True)
class CloudDeck:
    """Облачная колода — источник истины для шаблонов карточек."""
    id: UUID
    author_id: UUID
    name: str
    description: str
    type: str                # 'PUBLIC' или 'PRIVATE'
    downloaded: int = 0
    is_approved: bool = False    # Одобрена ли администратором (для PUBLIC)
    approved_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None 
    total_cards: Optional[int] = None
    previous_authors: List[UUID] = field(default_factory=list)
    
    def set_previous_authors(
            self,
            previous_authors: List[UUID]
         ) -> "CloudDeck":
            """Устанавливает значение previous_authors."""
            return replace(self, previous_authors=previous_authors)

    def approve(self) -> "CloudDeck":
        """Одобрить колоду (вызывает админ)."""
        return replace(self, is_approved=True, approved_at=datetime.now(timezone.utc))
    
    def set_total_cards(
        self,
        total_cards: int
     ) -> "CloudDeck":
        """Устанавливает значение total_cards."""
        return replace(self, total_cards=total_cards)
    

    def reject(self) -> "CloudDeck":
        """Отклонить колоду (вызывает админ)."""
        return replace(self, is_approved=False, approved_at=None)
    
    def change_type(self, type: str) -> "CloudDeck":
        """Устанавливает или меняет type колоды"""
        if type == "PUBLIC":
            return replace(self, type="PUBLIC", is_approved=False, approved_at=None)
        elif type == "PRIVATE":
            return replace(self, type="PRIVATE", is_approved=True, approved_at=None)
        else:
            raise ValueError(f"Invalid type: {type}")
