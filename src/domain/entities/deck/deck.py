from dataclasses import dataclass, field, replace
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
    desired_retention: float = 0.90
    maximum_interval: int = 36500
    color: str = "#4A90E2"
    total_cards: int = 0
    due_cards_count: int = 0

    def add_card(self, card: Card) -> "Deck":
        """Бизнес-метод: добавить карту, верни новую Deck."""
        if card.id in self.card_ids:
            raise ValueError("Карточка уже в колоде")
        new_card_ids = self.card_ids + [card.id]
        return Deck(
            id=self.id,
            name=self.name,
            description=self.description,
            desired_retention=self.desired_retention,
            maximum_interval=self.maximum_interval,
            color=self.color,
            user_id=self.user_id,
            card_ids=new_card_ids,
            due_cards_count=self.due_cards_count,
            total_cards=len(new_card_ids),
        )

    def with_updated_total_cards(self, new_total_cards: int) -> "Deck":
        """
        Создает новый экземпляр Deck с обновленным полем total_cards.
        """
        return replace(self, total_cards=new_total_cards)

    def with_updated_due_cards_count(self, new_due_cards_count: int) -> "Deck":
        """
        Создает новый экземпляр Deck с обновленным полем due_cards_count.
        """
        return replace(self, due_cards_count=new_due_cards_count)
