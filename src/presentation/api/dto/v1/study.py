from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.presentation.api.dto.v1.card import CardResponse
from src.domain.entities import Card


class NewToStudyRequest(BaseModel):
    deck_id: UUID = Field(
        description="id колоды из которой первести карточки в изучаемые"
    )
    total: int = Field(
        description="Количество карточек которые нужно добавить к изучению"
    )


class ReviewDueCardRequest(BaseModel):
    card_id: UUID
    rating: int = Field(
        ..., gt=0, le=4, description="1 - снова, 2 - сложно, 3 - хорошо, 4 - легко"
    )
    review_duration: int = Field(
        description="Длительность просмотра карточки в миллисекундах"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "card_id": "123e4567-e89b-12d3-a456-426614174000",
                    "rating": 3,
                    "review_duration": 5000
                }
            ]
        }
    }

class ReviewDueCardResponse(BaseModel):
    card: CardResponse
    success: bool = Field(
        description="Успешность повтора True - карточку больше повторять не нужно, False - отправить на повтор сегодня"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "card": {
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
                    },
                    "success": False
                }
            ]
        }
    }
