# src/presentation/api/dto/v1/cloud_deck.py
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

class DeckVisibility(str, Enum):
    """Тип видимости колоды"""
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class EnableSharingRequest(BaseModel):
    """
    Запрос на включение шаринга.
    """
    deck_id: UUID = Field(
        ...,
        description="UUID локальной колоды, которую нужно добавить в облако"
    )
    type: DeckVisibility = Field(
        default=DeckVisibility.PRIVATE,
        description="Тип видимости: PRIVATE (только по ссылке) или PUBLIC (в каталоге после модерации)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                     "deck_id": "123e4567-e89b-12d3-a456-426614174000",
                     "type": "PRIVATE"
                 },
                {
                     "deck_id": "123e4567-e89b-12d3-a456-426614174000",
                     "type": "PUBLIC"
                 }
             ]
        }
    }


class SyncStats(BaseModel):
    """Статистика синхронизации карточек"""
    added: int = Field(
        default=0,
        description="Количество добавленных карточек/шаблонов"
    )
    updated: int = Field(
        default=0,
        description="Количество обновленных карточек/шаблонов"
    )
    deleted: int = Field(
        default=0,
        description="Количество удаленных карточек/шаблонов"
    )


class EnableSharingResponse(BaseModel):
    """
    Ответ после успешного добавления в облако.
    """
    cloud_uuid: UUID = Field(
        ...,
        description="UUID облачной колоды"
    )
    status: str = Field(
        ...,
        description="Статус: ACTIVE (приватная) или PENDING_APPROVAL (на модерации)"
    )
    type: str = Field(
        ...,
        description="Текущий тип видимости"
    )
    
    # Статистика синхронизации карточек
    sync_stats: SyncStats = Field(
        default_factory=SyncStats,
        description="Статистика синхронизации карточек (добавлено, обновлено, удалено)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                     "cloud_uuid": "123e4567-e89b-12d3-a456-426614174000",
                     "status": "ACTIVE",
                     "type": "PRIVATE",
                     "sync_stats": {
                         "added": 10,
                         "updated": 5,
                         "deleted": 0
                     }
                 },
                 {
                     "cloud_uuid": "123e4567-e89b-12d3-a456-426614174000",
                     "status": "PENDING_APPROVAL",
                     "visibility": "DeckVisibility.PUBLIC",
                     "sync_stats": {
                         "added": 0,
                         "updated": 15,
                         "deleted": 2
                     }
                 }
             ]
        }
    }


class ImportDeckResponse(BaseModel):
    """
    Ответ после успешного импорта облачной колоды.
    """
    deck_id: str = Field(
         ...,
        description="UUID локальной колоды"
    )
    added: int = Field(
        default=0,
        description="Количество добавленных карточек"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                 {
                     "deck_id": "123e4567-e89b-12d3-a456-426614174000",
                     "added": 10
                 }
             ]
        }
    }

class ImportDeckRequest(BaseModel):
    """Запрос на импорт облачной колоды."""
    cloud_uuid: UUID = Field(
        ...,
        description="UUID облачной колоды для импорта"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cloud_uuid": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
    }
    
    
# class AuthorProfile(BaseModel):
#     """Профиль автора облачной колоды."""
#     user_id: str = Field(
#          ...,
#         description="UUID автора колоды",
#         examples=["123e4567-e89b-12d3-a456-426614174000"],
#      )
#     first_name: str = Field(
#          ...,
#         description="Имя автора",
#         examples=["John"],
#      )
#     last_name: str = Field(
#          ...,
#         description="Фамилия автора",
#         examples=["Doe"],
#      )
#     avatar_key: str = Field(
#          ...,
#         description="Ключ аватара (URL или путь к файлу)",
#         examples=["avatars/john_doe.jpg"],
#      )
#     bio: Optional[str] = Field(
#         None,
#         description="Биография автора",
#         examples=["Автор колоды по изучению английского языка"],
#      )


# class CloudDeckResponse(BaseModel):
#      """
#      Полный ответ с информацией об облачной колоде, включая все карточки и профиль автора.
#      """
#     id: str = Field(
#          ...,
#         description="UUID облачной колоды",
#         examples=["123e4567-e89b-12d3-a456-426614174000"],
#      )
#     name: str = Field(
#          ...,
#         description="Название колоды",
#         examples=["Английский 3000"],
#      )
#     description: str = Field(
#          ...,
#         description="Описание колоды",
#         examples=["3000 самых популярных слов в английском языке"],
#      )
#     total_cards: int = Field(
#          ...,
#         description="Общее количество карточек в колоде",
#         examples=[3000],
#      )
#     visibility: DeckVisibility = Field(
#          ...,
#         description="Тип видимости колоды: PUBLIC или PRIVATE",
#         examples=[DeckVisibility.PUBLIC],
#      )
#     is_approved: bool = Field(
#          ...,
#         description="Одобрена ли колода администратором",
#         examples=[True],
#      )
#     created_at: Optional[str] = Field(
#         None,
#         description="Дата создания колоды (ISO 8601)",
#         examples=["2024-01-01T00:00:00Z"],
#      )
#     updated_at: Optional[str] = Field(
#         None,
#         description="Дата последнего обновления колоды (ISO 8601)",
#         examples=["2024-01-15T12:00:00Z"],
#      )
    
#     author: AuthorProfile = Field(
#          ...,
#         description="Профиль автора колоды",
#      )
    
#     cards: List[CardResponse] = Field(
#         default_factory=list,
#         description="Список всех карточек колоды",
#      )

#     model_config = {
#          "json_schema_extra": {
#              "examples": [
#                  {
#                      "id": "123e4567-e89b-12d3-a456-426614174000",
#                      "name": "Английский 3000",
#                      "description": "3000 самых популярных слов в английском языке",
#                      "total_cards": 3000,
#                      "visibility": "PUBLIC",
#                      "is_approved": True,
#                      "created_at": "2024-01-01T00:00:00Z",
#                      "updated_at": "2024-01-15T12:00:00Z",
#                      "author": {
#                          "user_id": "123e4567-e89b-12d3-a456-426614174000",
#                          "first_name": "John",
#                          "last_name": "Doe",
#                          "avatar_key": "avatars/john_doe.jpg",
#                          "bio": "Автор колоды по изучению английского языка",
#                      },
#                      "cards": [
#                          {
#                              "id": "123e4567-e89b-12d3-a456-426614174001",
#                              "deck_id": "123e4567-e89b-12d3-a456-426614174000",
#                              "front": "Hello",
#                              "back": "Привет",
#                          },
#                          {
#                              "id": "123e4567-e89b-12d3-a456-426614174002",
#                              "deck_id": "123e4567-e89b-12d3-a456-426614174000",
#                              "front": "Goodbye",
#                              "back": "До свидания",
#                          },
#                      ],
#                  }
#              ]
#          }
#      }