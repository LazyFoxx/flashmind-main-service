from pydantic import Field
from typing import List

from pydantic import BaseModel

from src.domain.entities import Deck



# Получить список всех колод пользователя
class DeckResponse(BaseModel):
    id: str
    name: str
    description: str
    total_cards: int
    repeat_cards: int
    
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "UUID",
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                    "total_cards": 10,
                    "repeat_cards": 3,
                    "desired_retention": 0.90,
                    "maximum_interval": 36500,
                    "color": "#4A90E2",
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
            total_cards=deck.total_cards or 0,
            repeat_cards=deck.due_cards_count or 0,
            desired_retention=deck.desired_retention,
            maximum_interval=deck.maximum_interval,
            color=deck.color,
         )

class DeckResponseUpdate(BaseModel):
    id: str
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "UUID",
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                    "desired_retention": 0.90,
                    "maximum_interval": 36500,
                    "color": "#4A90E2",
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
            total_cards=deck.total_cards or 0,
            repeat_cards=deck.due_cards_count or 0,
            desired_retention=deck.desired_retention,
            maximum_interval=deck.maximum_interval,
            color=deck.color,
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
                             "desired_retention": 0.90,
                             "maximum_interval": 36500,
                             "color": "#4A90E2",
                             },
                         {
                             "id": "UUID",
                             "name": "Математика 101",
                             "description": "Основы математики, арифметика и геометрия",
                             "total_cards": 15,
                             "repeat_cards": 3,
                             "desired_retention": 0.90,
                             "maximum_interval": 36500,
                             "color": "#4A90E2",
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

