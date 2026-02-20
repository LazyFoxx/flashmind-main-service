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


# Получить список всех колод пользователя
class DeckResponseTotalCards(BaseModel):
    id: str
    name: str
    description: str
    total_cards: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "UUID",
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                    "total_cards": 10,
                }
            ]
        }
    }

    @classmethod
    def from_entity(cls, deck: Deck) -> "DeckResponseTotalCards":
        if deck.total_cards is None:
            return cls(
                id=str(deck.id),
                name=deck.name,
                description=deck.description,
                total_cards=0,
            )

        return cls(
            id=str(deck.id),
            name=deck.name,
            description=deck.description,
            total_cards=deck.total_cards,
        )


class GetUserDecksResponse(BaseModel):
    decks: List[DeckResponseTotalCards]  # используем List для списка объектов

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
                        },
                        {
                            "id": "UUID",
                            "name": "Математика 101",
                            "description": "Основы математики, арифметика и геометрия",
                            "total_cards": 15,
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
