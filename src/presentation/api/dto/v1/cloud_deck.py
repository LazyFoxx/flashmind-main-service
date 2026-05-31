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