from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.domain.entities import Card


# создание карточки
class CreateCardRequest(BaseModel):
    deck_id: UUID
    front: str
    back: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                    "front": "Любимый Настин напиток",
                    "back": "Тот что с сарахозаменителем",
                }
            ]
        }
    }


class CardResponse(BaseModel):
    id: str
    deck_id: str
    front: str
    back: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                    "front": "Любимый Настин напиток",
                    "back": "Тот что с сарахозаменителем",
                }
            ]
        }
    }


# обновление карточки
class UpdateCardRequest(BaseModel):
    front: str
    back: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "front": "Любовь",
                    "back": "Это когда она в тебя высмаркивается",
                }
            ]
        }
    }


# получить список карточек
class CardLightResponse(BaseModel):
    id: str
    deck_id: str
    front: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                    "front": "Любимый Настин напиток",
                }
            ]
        }
    }


class CardListResponse(BaseModel):
    cards: List[CardLightResponse]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cards": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                            "front": "Любовь",
                        },
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174002",
                            "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                            "front": "Смех",
                        },
                    ],
                    "total": 100,
                    "page": 1,
                    "per_page": 10,
                }
            ]
        }
    }
