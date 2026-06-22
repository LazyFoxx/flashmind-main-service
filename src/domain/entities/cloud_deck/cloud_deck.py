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

    def approve(self) -> "CloudDeck":
        """Одобрить колоду (вызывает админ)."""
        return replace(self, is_approved=True, approved_at=datetime.now(timezone.utc))
    

    def reject(self) -> "CloudDeck":
        """Отклонить колоду (вызывает админ)."""
        return replace(self, is_approved=False, approved_at=None)
    
    def change_type(self, type: str) -> "CloudDeck":
        """устанавливает или меняет type колоды"""

        if type == "PUBLIC":
            return self._copy(type="PUBLIC", is_approved=False, approved_at=None)
        elif type == "PRIVATE":
            return self._copy(type="PRIVATE", is_approved=True, approved_at=None)
        else:
            raise