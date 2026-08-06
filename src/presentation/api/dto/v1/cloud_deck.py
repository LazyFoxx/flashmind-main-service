# src/presentation/api/dto/v1/cloud_deck.py
from enum import Enum
from typing import List, Optional
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
    
    updated: int = Field(
            default=0,
            description="Количество обновленных карточек"
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                 {
                     "deck_id": "123e4567-e89b-12d3-a456-426614174000",
                     "added": 10,
                     "updated": 7,
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
    
    
class AuthorProfile(BaseModel):
    """Профиль автора облачной колоды."""
    user_id: str = Field(
         ...,
        description="UUID автора колоды",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
     )
    first_name: str = Field(
         ...,
        description="Имя автора",
        examples=["John"],
     )
    last_name: str = Field(
         ...,
        description="Фамилия автора",
        examples=["Doe"],
     )
    avatar_url: str = Field(
         ...,
        description="Ключ аватара (URL или путь к файлу)",
        examples=["avatars/john_doe.jpg"],
     )
    bio: Optional[str] = Field(
        None,
        description="Биография автора",
        examples=["Автор колоды по изучению английского языка"],
     )



class CloudCardResponse(BaseModel):
    id: str
    front: str
    back: str

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


class CloudDeckResponse(BaseModel):
    """
    Полный ответ с информацией об облачной колоде, включая все карточки и профиль автора.
    """
    id: str = Field(
         ...,
        description="UUID облачной колоды",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
     )
    name: str = Field(
         ...,
        description="Название колоды",
        examples=["Английский 3000"],
     )
    description: str = Field(
         ...,
        description="Описание колоды",
        examples=["3000 самых популярных слов в английском языке"],
     )
    total_cards: int = Field(
         ...,
        description="Общее количество карточек в колоде",
        examples=[3000],
     )
    last_synced_at: Optional[str] = Field(
        None,
        description="Дата последнего обновления колоды (ISO 8601)",
        examples=["2024-01-15T12:00:00Z"],
     )
    
    downloaded: int = Field(
         ...,
        description="Общее количество карточек в колоде",
        examples=[3000],
     )
    
    author: AuthorProfile = Field(
         ...,
        description="Профиль автора колоды",
     )
    
    cards: List[CloudCardResponse] = Field(
        default_factory=list,
        description="Список всех карточек колоды",
     )

    model_config = {
         "json_schema_extra": {
             "examples": [
                 {
                     "id": "123e4567-e89b-12d3-a456-426614174000",
                     "name": "Английский 3000",
                     "description": "3000 самых популярных слов в английском языке",
                     "total_cards": 3000,
                     "last_synced_at": "2024-01-15T12:00:00Z",
                     "downloaded": 0,
                     "author": {
                         "user_id": "123e4567-e89b-12d3-a456-426614174000",
                         "first_name": "John",
                         "last_name": "Doe",
                         "avatar_url": "avatars/john_doe.jpg",
                         "bio": "Автор колоды по изучению английского языка",
                     },
                     "cards": [
                         {
                             "id": "123e4567-e89b-12d3-a456-426614174001",
                             "front": "Hello",
                         },
                         {
                             "id": "123e4567-e89b-12d3-a456-426614174002",
                             "front": "Goodbye",
                         },
                     ],
                 }
             ]
         }
     }
    



class AuthorProfile(BaseModel):
    """Профиль автора облачной колоды."""
    user_id: str = Field(
          ...,
        description="UUID автора колоды",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
      )
    first_name: str = Field(
          ...,
        description="Имя автора",
        examples=["John"],
      )
    last_name: str = Field(
          ...,
        description="Фамилия автора",
        examples=["Doe"],
      )
    avatar_url: str = Field(
          ...,
        description="ссылка на аватар",
        examples=["avatars/john_doe.jpg"],
      )
    bio: Optional[str] = Field(
        None,
        description="Биография автора",
        examples=["Автор колоды по изучению английского языка"],
      )

    @classmethod
    def from_user(cls, user) -> "AuthorProfile":
        """Создать AuthorProfile из сущности User.
        
        Args:
            user: сущность domain.entities.user.user.User
            
        Returns:
            AuthorProfile с данными пользователя
        """
        return cls(
            user_id=str(user.user_id),
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
        )


class CloudCardResponse(BaseModel):
    id: str
    front: str

    @classmethod
    def from_entity(cls, card) -> "CloudCardResponse":
        """Создать CloudCardResponse из сущности CloudCardTemplate.
        
        Args:
            card: сущность domain.entities.cloud_card.cloud_card.CloudCardTemplate
            
        Returns:
            CloudCardResponse с данными карточки
        """
        return cls(
            id=str(card.id),
            front=card.front,
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                     "id": "123e4567-e89b-12d3-a456-426614174000",
                     "front": "Любимый Настин напиток",
                 }
             ]
        }
     }


class CloudDeckResponse(BaseModel):
    """
    Полный ответ с информацией об облачной колоде, включая все карточки и профиль автора.
    """
    id: str = Field(
          ...,
        description="UUID облачной колоды",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
      )
    name: str = Field(
          ...,
        description="Название колоды",
        examples=["Английский 3000"],
      )
    description: str = Field(
          ...,
        description="Описание колоды",
        examples=["3000 самых популярных слов в английском языке"],
      )
    total_cards: int = Field(
          ...,
        description="Общее количество карточек в колоде",
        examples=[3000],
      )
    last_synced_at: Optional[str] = Field(
        None,
        description="Дата последнего обновления колоды (ISO 8601)",
        examples=["2024-01-15T12:00:00Z"],
      )
    
    downloaded: int = Field(
          ...,
        description="Количество загруженных карточек",
        examples=[3000],
      )
    
    author: AuthorProfile = Field(
          ...,
        description="Профиль автора колоды",
      )
    
    cards: List[CloudCardResponse] = Field(
        default_factory=list,
        description="Список всех карточек колоды",
      )

    @classmethod
    def from_entity(cls, deck, author, cards) -> "CloudDeckResponse":
        """Создать CloudDeckResponse из сущности CloudDeck.
        
        Args:
            deck: сущность domain.entities.cloud_deck.cloud_deck.CloudDeck
            author: сущность domain.entities.user.user.User (автор колоды)
            cards: список сущностей CloudCardTemplate (опционально)
            
        Returns:
            CloudDeckResponse с данными колоды
        """

        return cls(
            id=str(deck.id),
            name=deck.name,
            description=deck.description,
            total_cards=len(cards) if cards else deck.downloaded,
            last_synced_at=deck.last_synced_at.isoformat() if deck.last_synced_at else None,
            downloaded=deck.downloaded,
            author=AuthorProfile.from_user(author),
            cards=[CloudCardResponse.from_entity(card) for card in cards],
        )

    model_config = {
          "json_schema_extra": {
              "examples": [
                  {
                      "id": "123e4567-e89b-12d3-a456-426614174000",
                      "name": "Английский 3000",
                      "description": "3000 самых популярных слов в английском языке",
                      "total_cards": 3000,
                      "last_synced_at": "2024-01-15T12:00:00Z",
                      "downloaded": 0,
                      "author": {
                          "user_id": "123e4567-e89b-12d3-a456-426614174000",
                          "first_name": "John",
                          "last_name": "Doe",
                          "avatar_url": "avatars/john_doe.jpg",
                          "bio": "Автор колоды по изучению английского языка",
                      },
                      "cards": [
                          {
                              "id": "123e4567-e89b-12d3-a456-426614174001",
                              "front": "Hello",
                          },
                          {
                              "id": "123e4567-e89b-12d3-a456-426614174002",
                              "front": "Goodbye",
                          },
                      ],
                  }
              ]
          }
      }
    
    
class CloudTemplateCardResponse(BaseModel):
    id: str
    front: str
    back: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "front": "Любимый Настин напиток",
                    "back": "Тот что с сарахозаменителем",
                }
            ]
        }
    }

class PublicDeckPreviewResponse(BaseModel):
    """Превью публичной облачной колоды."""
    
    id: str = Field(
        ...,
        description="UUID облачной колоды",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    name: str = Field(
        ...,
        description="Название колоды",
        examples=["Английский 3000"],
    )
    total_cards: int = Field(
        ...,
        description="Общее количество карточек в колоде",
        examples=[3000],
    )
    downloaded: int = Field(
        default=0,
        description="Количество загруженных карточек",
        examples=[0],
    )
    last_synced_at: Optional[str] = Field(
        None,
        description="Дата последнего обновления колоды (ISO 8601)",
        examples=["2024-01-15T12:00:00Z"],
    )
    author: AuthorProfile = Field(
        ...,
        description="Профиль автора колоды",
    )
    
    @classmethod
    def from_entity(cls, deck) -> "PublicDeckPreviewResponse":
        """Создать PublicDeckPreviewResponse из  preview_deck."""
        return cls(
            id=str(deck.id),
            name=deck.name,
            description=deck.description,
            total_cards=deck.total_cards,
            downloaded=deck.downloaded,
            last_synced_at=str(deck.last_synced_at),
            author=AuthorProfile(user_id=deck.author_id,
                                 first_name=deck.author_first_name,
                                 last_name=deck.author_last_name,
                                 avatar_url=deck.author_avatar_url),
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Английский 3000",
                    "total_cards": 3000,
                    "downloaded": 0,
                    "last_synced_at": "2024-01-15T12:00:00Z",
                    "author": {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "first_name": "John",
                        "last_name": "Doe",
                        "avatar_url": "avatars/john_doe.jpg",
                    },
                }
            ]
        }
    }
    


class PublicDecksResponse(BaseModel):
    """
    Список публичных колод.
    """
    
    decks: List[PublicDeckPreviewResponse] = Field(
        default_factory=list,
        description="Список публичных облачных колод",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "decks": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Английский 3000",
                            "description": "3000 самых популярных слов",
                            "total_cards": 3000,
                            "downloaded": 0,
                            "last_synced_at": "2024-01-15T12:00:00Z",
                            "author": {
                                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                                "first_name": "John",
                                "last_name": "Doe",
                                "avatar_url": "avatars/john_doe.jpg",
                            },
                        },
                    ],
                }
            ]
        }
    }


class TakeOwnershipRequest(BaseModel):
    deck_id: UUID = Field(
        ...,
        description="UUID локальной колоды которую нужно отвязать от облака"
    )


class TakeOwnershipResponse(BaseModel):
    cloud_uuid: str = Field(
        ...,
        description="UUID новой облачной колоды где пользователь становится автором"
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
    

class CanTakeOwnershipResponse(BaseModel):
    description_changed: bool = Field(
           ...,
        description="Изменил ли пользователь описание колоды"
       )

    cards_needed_count: int = Field(
           ...,
        description="Сколько еще карточек нужно добавить чтобы достичь 20%"
       )