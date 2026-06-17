from dataclasses import dataclass, field, replace
from typing import List, Optional
from uuid import UUID

from src.domain.entities.card.card import Card


@dataclass(slots=True, frozen=True)
class Deck:
    """
    Колода пользователя. Может быть локальной или привязанной к облаку."
    """

    id: UUID
    name: str
    description: str
    user_id: UUID
    card_ids: List[UUID] = field(default_factory=list)
    desired_retention: float = 0.92
    maximum_interval: int = 365
    color: str = "#4A90E2"
    total_cards: int = 0
    due_cards_count: int = 0
    
    cloud_deck_id: Optional[UUID] = None    # Ссылка на облачную колоду (nullable)
    is_cloud_deck: bool = False             # Это облачная колода?
    cloud_type: Optional[str] = None        # 'PUBLIC' | 'PRIVATE' (только для cloud)
    is_approved: bool = False               # Одобрена админом (только для cloud)
    author_id: Optional[UUID] = None

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
    
    def with_updated_settings(
        self,
        new_desired_retention: float,
        new_maximum_interval: int,
        new_color: str,
     ) -> "Deck":
        """
        Создает новый экземпляр Deck с обновленными полями настроек.
        """
        return replace(
            self,
            desired_retention=new_desired_retention,
            maximum_interval=new_maximum_interval,
            color=new_color,
         )
    
    def to_cloud(
        self,
        cloud_deck_id: UUID,
        cloud_type: str,
        is_approved: bool,
        author_id: UUID
     ) -> "Deck":
        """
        привязывает колоду к облачной колоде.
        """
        return replace(
            self,
            cloud_deck_id=cloud_deck_id,
            is_cloud_deck=True,
            cloud_type=cloud_type,
            is_approved=is_approved,
            author_id=author_id,
         )

