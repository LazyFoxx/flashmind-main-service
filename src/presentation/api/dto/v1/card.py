from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.entities import Card


# создание карточки
class CreateCardRequest(BaseModel):
    deck_id: UUID
    title: str
    front: Any
    back: Any
    hint1: Optional[str] = Field(default=None, min_length=3, max_length=120)
    hint2: Optional[str] = Field(default=None, min_length=3, max_length=120)

    model_config = {
          "json_schema_extra": {
              "examples": [
                  {
                      "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                      "title": "Любимый напиток",
                      "front": [{"type": "text", "value": "Любимый Настин напиток"}],
                      "back": [{"type": "text", "value": "Тот что с сарахозаменителем"}],
                      "hint1": "Подсказка 1",
                      "hint2": "Подсказка 2",
                  }
              ]
          }
      }


# обновление карточки (partial update — передавай только то, что хочешь изменить)
class UpdateCardRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=120)
    front: Optional[Any] = Field(default=None)
    back: Optional[Any] = Field(default=None)
    hint1: Optional[str] = Field(default=None, min_length=3, max_length=120)
    hint2: Optional[str] = Field(default=None, min_length=3, max_length=120)
    is_suspended: Optional[bool] = Field(default=None)

    model_config = {
       "json_schema_extra": {
           "examples": [
               {
                   "front": [{"type": "text", "value": "Новый фронт"}],
                   "is_suspended": True,
               }
           ]
       }
    }


# универсальный полный ответ карточки
class CardResponse(BaseModel):
    id: str = Field(
        description="UUID карточки",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
     )
    deck_id: str = Field(
        description="UUID колоды",
        examples=["123e4567-e89b-12d3-a456-426614174001"],
     )
    title: str = Field(
        description="Заголовок карточки",
        examples=["Любимый напиток"],
     )
    front: Any = Field(
        description="Содержимое лицевой стороны (JSON)",
        examples=[[{"type": "text", "value": "Любимый Настин напиток"}]],
     )
    back: Any = Field(
        description="Содержимое обратной стороны (JSON)",
        examples=[[{"type": "text", "value": "Тот что с сарахозаменителем"}]],
     )
    hint1: Optional[str] = Field(
        default=None,
        description="Первая подсказка",
        examples=["Подсказка 1"],
     )
    hint2: Optional[str] = Field(
        default=None,
        description="Вторая подсказка",
        examples=["Подсказка 2"],
     )
    difficulty: Optional[float] = Field(
        default=None,
        description="Сложность (FSRS)",
        examples=[3.32344],
     )
    stability: Optional[float] = Field(
        default=None,
        description="Стабильность (FSRS)",
        examples=[1.23434],
     )
    in_learning: bool = Field(
        default=False,
        description="В процессе изучения",
        examples=[False],
     )
    card_template_id: Optional[str] = Field(
        default=None,
        description="UUID шаблона из облака (если карточка синхронизирована)",
        examples=["123e4567-e89b-12d3-a456-426614174002"],
     )
    created_at: Optional[str] = Field(
        default=None,
        description="Дата создания (ISO 8601)",
        examples=["2024-01-15T12:00:00Z"],
     )
    is_suspended: bool = Field(
        default=False,
        description="Отложенная карточка",
        examples=[False],
    )

    @classmethod
    def from_entity(cls, card: Card) -> "CardResponse":
        """Создать CardResponse из сущности Card."""
        return cls(
            id=str(card.id),
            deck_id=str(card.deck_id),
            title=card.title,
            front=card.front,
            back=card.back,
            hint1=card.hint1,
            hint2=card.hint2,
            difficulty=card.difficulty,
            stability=card.stability,
            in_learning=card.in_learning,
            card_template_id=str(card.card_template_id) if card.card_template_id else None,
            created_at=card.created_at.isoformat() if card.created_at else None,
            is_suspended=card.is_suspended,
         )

    model_config = {
          "json_schema_extra": {
              "examples": [
                  {
                      "id": "123e4567-e89b-12d3-a456-426614174000",
                      "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                      "title": "Любимый напиток",
                      "front": [{"type": "text", "value": "Любимый Настин напиток"}],
                      "back": [{"type": "text", "value": "Тот что с сарахозаменителем"}],
                      "hint1": "Подсказка 1",
                      "hint2": "Подсказка 2",
                      "difficulty": 3.32344,
                      "stability": 1.23434,
                      "in_learning": False,
                      "card_template_id": None,
                      "created_at": "2024-01-15T12:00:00Z",
                      "is_suspended": False
                  }
              ]
          }
      }


# список карточек
class CardListResponse(BaseModel):
    cards: List[CardResponse] = Field(
        default_factory=list,
        description="Список карточек",
     )

    model_config = {
          "json_schema_extra": {
              "examples": [
                  {
                      "cards": [
                          {
                              "id": "123e4567-e89b-12d3-a456-426614174000",
                              "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                              "title": "Любовь",
                              "front": [{"type": "text", "value": "Любимый Настин напиток"}],
                              "back": [{"type": "text", "value": "Тот что с сарахозаменителем"}],
                              "hint1": None,
                              "hint2": None,
                              "difficulty": 3.32344,
                              "stability": 1.23434,
                              "in_learning": True,
                              "card_template_id": None,
                              "created_at": "2024-01-15T12:00:00Z",
                              "is_suspended": False
                          }
                      ],
                  }
              ]
          }
      }

class ReviewHistoryItem(BaseModel):
    """Элемент истории ревью карточки."""
    review_datetime: str = Field(description="Дата и время ревью (ISO 8601)")
    rating: int = Field(description="Ответ: 1: Again, 2: Hard, 3: Good, 4: Easy")
    difficulty: float = Field(description="Сложность после ревью")
    stability: float = Field(description="Стабильность после ревью")
    review_duration_ms: int = Field(description="Длительность ревью в миллисекундах")




class CardDetailResponse(BaseModel):
    """Расширенный ответ карточки с историей ревью."""
    
    card: CardResponse
    
    last_review_datetime: Optional[str] = Field(
        default=None,
        description="Дата последнего повтора (ISO 8601)",
    )
    next_review_datetime: Optional[str] = Field(
        default=None,
        description="Дата следующего повтора (ISO 8601)",
    )
    review_history: List[ReviewHistoryItem] = Field(
        default_factory=list,
        description="История ревью карточки",
    )
    
    
    @classmethod
    def from_entity(cls, card: Card, review_stats=None) -> "CardDetailResponse":
        """Создать CardDetailResponse из сущности Card."""
        
        review_history = []
        if review_stats and review_stats.review_history:
            review_history = [
                ReviewHistoryItem(
                    review_datetime=item.review_datetime.isoformat() if item.review_datetime else None,
                    rating=item.rating,
                    difficulty=item.difficulty,
                    stability=item.stability,
                    review_duration_ms=item.review_duration_ms,
                 )
                for item in review_stats.review_history
             ]
            
        return cls(
            last_review_datetime=review_stats.last_review_datetime.isoformat() if review_stats and review_stats.last_review_datetime else None,
            next_review_datetime=review_stats.next_review_datetime.isoformat() if review_stats and review_stats.next_review_datetime else None,
            review_history=review_history,
            card=CardResponse.from_entity(card=card)
         )
    
    model_config = {
              "json_schema_extra": {
                  "examples": [{
                        "card": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "deck_id": "123e4567-e89b-12d3-a456-426614174001",
                            "title": "Любимый напиток",
                            "front": [{"type": "text", "value": "Любимый Настин напиток"}],
                            "back": [{"type": "text", "value": "Тот что с сарахозаменителем"}],
                            "hint1": "Подсказка 1",
                            "hint2": "Подсказка 2",
                            "difficulty": 3.32344,
                            "stability": 1.23434,
                            "in_learning": False,
                            "is_suspended": False,
                            "card_template_id": None,
                            "created_at": "2024-01-15T12:00:00Z"
                        },
                        "last_review_datetime": "2024-01-20T15:30:00Z",
                        "next_review_datetime": "2024-01-22T10:00:00Z",
                        "review_history": [
                            {
                                "review_datetime": "2024-01-10T10:00:00Z",
                                "rating": 3,
                                "difficulty": 2.8,
                                "stability": 1.5,
                                "review_duration_ms": 5000
                            },
                            {
                                "review_datetime": "2024-01-15T14:00:00Z",
                                "rating": 2,
                                "difficulty": 3.0,
                                "stability": 1.2,
                                "review_duration_ms": 8000
                            },
                            {
                                "review_datetime": "2024-01-20T15:30:00Z",
                                "rating": 3,
                                "difficulty": 3.3,
                                "stability": 1.8,
                                "review_duration_ms": 6000
                            }
                        ]
                    }
                ]
              }
          }