from typing import List
from uuid import UUID

from pydantic import BaseModel

from src.domain.entities import Card


# создание колоды
class CreateCardRequest(BaseModel):
    deck_id: UUID
    front: str
    back: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "deck_id": "UUID_STR",
                    "front": "Любовь",
                    "back": "Это когда она в тебя высмаркивается",
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
                    "id": "UUID",
                    "name": "Английский 3000",
                    "description": "Тут собраны 3000 самых популярных слов в английском языке",
                }
            ]
        }
    }
