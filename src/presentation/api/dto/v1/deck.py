from pydantic import Field
from typing import List

from pydantic import BaseModel

from src.domain.entities import Deck


# создание колоды
class CreateDeckRequest(BaseModel):
    name: str
    description: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                }
            ]
        }
    }


class DeckResponse(BaseModel):
    id: str
    name: str
    description: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "UUID",
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                }
            ]
        }
    }

    @classmethod
    def from_entity(cls, deck: Deck) -> "DeckResponse":
        return cls(
            id=str(deck.id),
            name=deck.name,
            description=deck.description,
        )


class DeckSettings(BaseModel):
    desired_retention: float = Field(
         ...,
        ge=0.85,
        le=0.95,
        description="Целевая удержание карт (от 0.0 до 1.0). 0.90 = 90% удержание.",
        examples=[0.90, 0.95],
     )
    maximum_interval: int = Field(
         ...,
        ge=60,
        le=36500,
        description="Максимальный интервал повторения в днях. Не может превышать 36500 дней.",
        examples=[365, 36500],
     )
    color: str = Field(
         ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Цвет колоды в формате HEX. Например, #4A90E2.",
        examples=["#4A90E2", "#FF5733"],
     )

    
class DeckSettingsOutput(DeckSettings):
    id: str
    
    model_config = {
         "json_schema_extra": {
             "examples": [
                 {
                     "id": "UUID",
                     "desired_retention": 0.90,
                     "maximum_interval": 36500,
                     "color": "#4A90E2",
                 }
             ]
         }
     }


# Получить список всех колод пользователя
class DeckResponseTotalCards(BaseModel):
    id: str
    name: str
    description: str
    total_cards: int
    repeat_cards: int
    settings: DeckSettings

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "UUID",
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                    "total_cards": 10,
                    "repeat_cards": 3,
                     "settings": {
                         "desired_retention": 0.90,
                         "maximum_interval": 36500,
                         "color": "#4A90E2",
                     },
        }
                    ]
                }
        }

    @classmethod
    def from_entity(cls, deck: Deck) -> "DeckResponseTotalCards":
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
         )


class GetUserDecksResponse(BaseModel):
    decks: List[DeckResponseTotalCards]     # используем List для списка объектов
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
                         },
                         {
                             "id": "UUID",
                             "name": "Математика 101",
                             "description": "Основы математики, арифметика и геометрия",
                             "total_cards": 15,
                             "repeat_cards": 3,
                             "settings": {
                                 "desired_retention": 0.90,
                                 "maximum_interval": 36500,
                                 "color": "#4A90E2",
                             },
                         },
            ]
        }
             ]
    }
     }


# изменение полей колоды (update)
class UpdateDeckRequest(CreateDeckRequest):
    pass


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

