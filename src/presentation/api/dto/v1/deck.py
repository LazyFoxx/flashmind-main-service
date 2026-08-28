from uuid import UUID

from pydantic import Field
from typing import List, Optional

from pydantic import BaseModel

from src.domain.entities import Deck
from src.presentation.api.dto.v1.card import CardResponse


class DeckSettings(BaseModel):
    """Настройки колоды."""
    desired_retention: float = Field(
        ...,
        ge=0.85,
        le=0.95,
        description="Целевая удержание карт (от 0.85 до 0.95). 0.90 = 90% удержание.",
        examples=[0.90, 0.95],
    )
    maximum_interval: int = Field(
        ...,
        ge=30,
        le=36500,
        description="Максимальный интервал повторения в днях. Не может превышать 740 дней.",
        examples=[365, 730],
    )
    color: str = Field(
        ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Цвет колоды в формате HEX. Например, #4A90E2.",
        examples=["#4A90E2", "#FF5733"],
    )


class CloudDeckInfo(BaseModel):
    """Информация об облачной колоде."""
    cloud_deck_id: Optional[str] = Field(
        None,
        description="UUID облачной колоды (если привязана)",
        examples=["00000000-0000-0000-0000-000000000000"],
    )
    is_cloud_deck: bool = Field(
        False,
        description="Является ли колода облачной",
        examples=[False],
    )
    cloud_type: Optional[str] = Field(
        None,
        description="Тип облачной колоды: 'PUBLIC' или 'PRIVATE'",
        examples=["PUBLIC", "PRIVATE"],
    )
    is_approved: bool = Field(
        False,
        description="Одобрена ли облачная колода админом",
        examples=[False],
    )
    is_author: bool = Field(
        False,
        description="Является ли пользователь владельцем облачной колоды",
        examples=[False],
    )
    
    needs_sync: bool = Field(
        False,
        description="Необходимость синхранизации колоды",
        examples=[False],
    )


class DeckResponse(BaseModel):
    """Ответ с информацией о колоде."""
    id: str
    name: str
    description: str
    total_cards: int
    repeat_cards: int
    settings: DeckSettings
    cloud_info: CloudDeckInfo
    cards_on_study: List[CardResponse] = Field(
        default_factory=list,
        description="Карточки на обучение на сегодня для этой колоды",
    )

    @classmethod
    def from_entity(cls, deck: Deck, user_id: UUID, cards_on_study: Optional[List[CardResponse]] = None) -> "DeckResponse":
        
        return cls(
            id=str(deck.id),
            name=deck.name,
            description=deck.description,
            total_cards=deck.total_cards or 0,
            repeat_cards=deck.due_cards_count or 0,
            settings=DeckSettings(
                desired_retention=deck.desired_retention,
                maximum_interval=deck.maximum_interval,
                color=deck.color,
            ),
            cloud_info = CloudDeckInfo(
                cloud_deck_id=str(deck.cloud_deck_id) if deck.cloud_deck_id else None,
                is_cloud_deck=deck.is_cloud_deck,
                cloud_type=deck.cloud_type,
                is_approved=deck.is_approved,
                is_author=True if user_id == deck.author_id or deck.is_cloud_deck == False else False,
                needs_sync=deck.needs_sync,
            ),
            cards_on_study=cards_on_study or [],
        )


class UserDecksResponse(BaseModel):
    decks: List[DeckResponse]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "decks": [
                        {
                            "id": "UUID",
                            "name": "Английский 3000",
                            "description": "Тут собраны 3000 самых популярных слов в английском языке",
                            "total_cards": 11,
                            "repeat_cards": 3,
                            "settings": {
                                "desired_retention": 0.90,
                                "maximum_interval": 36500,
                                "color": "#4A90E2",
                            },
                            "cloud_info": {
                                "cloud_deck_id": None,
                                "is_cloud_deck": False,
                                "cloud_type": None,
                                "is_approved": False,
                                "author_id": None,
                                "needs_sync": False,
                            },
                             "cards_on_study": [
                                {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "deck_id": "UUID",
                                "title": "Любовь",
                                "front": "Что такое любовь",
                                "back": "Это когда она в тебя высмаркивается",
                                "hint1": None,
                                "hint2": None,
                                "difficulty": 3.32344,
                                "stability": 1.23434,
                                "in_learning": True,
                                "card_template_id": None,
                                "created_at": "2024-01-15T12:00:00Z",
                                "updated_at": "2024-01-16T10:30:00Z",
                                }
                            ],
                        },
                    ]
                }
            ]
        }
    }

# изменение полей колоды (update)
class UpdateDeckRequest(BaseModel):
    name: str
    description: str
    desired_retention: float = Field(
         ...,
        ge=0.85,
        le=0.95,
        description="Целевая удержание карт (от 0.0 до 1.0). 0.90 = 90% удержание.",
        examples=[0.90, 0.95],
     )
    maximum_interval: int = Field(
         ...,
        ge=30,
        le=740,
        description="Максимальный интервал повторения в днях. Не может превышать 36500 дней.",
        examples=[365, 740],
     )
    color: str = Field(
         ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Цвет колоды в формате HEX. Например, #4A90E2.",
        examples=["#4A90E2", "#FF5733"],
     )

# создание колоды
class CreateDeckRequest(BaseModel):
    name: str
    description: str
    color: str = Field(
         ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Цвет колоды в формате HEX. Например, #4A90E2.",
        examples=["#4A90E2", "#FF5733"],
     )
    

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                    "color": "#4A90E2",
                }
            ]
        }
    }

# обработка ошибок
class ErrorMessageResponse(BaseModel):
    message: str
    model_config = {
         "json_schema_extra": {
             "examples": [
                 {
                     "message": "Описание ошибки",
                 },
             ]
         }
     }

