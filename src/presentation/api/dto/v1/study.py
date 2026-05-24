from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities import Card


class NewToStudyRequest(BaseModel):
    deck_id: UUID = Field(
        description="id колоды из которой первести карточки в изучаемые"
    )
    total: int = Field(
        description="Количество карточек которые нужно добавить к изучению"
    )


# базовая модель карточки в обучении
class StudyCardResponse(BaseModel):
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

    @classmethod
    def from_entity(cls, card: Card) -> "StudyCardResponse":
        return cls(
            id=str(card.id),
            deck_id=str(card.deck_id),
            front=card.front,
            back=card.back,
        )


class StudyCardListResponse(BaseModel):
    cards: List[StudyCardResponse]
    total: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cards": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                            "front": "Любовь",
                            "back": "Это просто",
                        },
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174002",
                            "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                            "front": "Смех",
                            "back": "Ахахахаа ору",
                        },
                    ],
                    "total": 100,
                }
            ]
        }
    }


class StudyCardListWithStatsResponse(BaseModel):
    total: int
    in_learning: int
    learned: int
    learning_today: int
    cards: List[StudyCardResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cards": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                            "front": "Любовь",
                            "back": "Это просто",
                        },
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174002",
                            "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                            "front": "Смех",
                            "back": "Ахахахаа ору",
                        },
                    ],
                    "total": 100,
                    "in_learning": 30,
                    "learned": 30,
                    "learning_today": 15,
                }
            ]
        }
    }


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
