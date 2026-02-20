from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from src.domain.entities.card.card import Card


@dataclass(slots=True, frozen=True)
class Deck:
    """
    Доменная сущность колоды.
    """

    id: UUID
    name: str
    description: str
    user_id: UUID
    card_ids: List[UUID] = field(default_factory=list)
    total_cards: Optional[int] = None

    def add_card(self, card: Card) -> "Deck":
        """Бизнес-метод: добавить карту, верни новую Deck."""
        if card.id in self.card_ids:
            raise ValueError("Карточка уже в колоде")
        new_card_ids = self.card_ids + [card.id]
        return Deck(
            id=self.id,
            name=self.name,
            description=self.description,
            user_id=self.user_id,
            card_ids=new_card_ids,
        )
