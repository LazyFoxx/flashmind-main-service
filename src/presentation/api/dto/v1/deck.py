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
class GetUserDecksResponse(BaseModel):
    decks: List[DeckResponse]  # используем List для списка объектов

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "decks": [
                        {
                            "id": "UUID",
                            "name": "Английский 3000",
                            "description": "Тут собраны 3000 самых популярных слов в английском языке",
                        },
                        {
                            "id": "UUID",
                            "name": "Математика 101",
                            "description": "Основы математики, арифметика и геометрия",
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
                    "message": "У пользователя нет такой колоды",
                },
                {
                    "message": "Карточка с таким front уже существует в этой колоде",
                },
            ]
        }
    }
