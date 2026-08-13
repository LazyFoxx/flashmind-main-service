from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any
from uuid import UUID
from datetime import datetime
import json

from src.domain.entities import CloudDeck, User
from src.application.use_cases.users.get_user_profile.dto import GetProfileUserOutput


@dataclass(frozen=True, slots=True)
class PublicDeckPreview:
    """Легкосериализуемая структура для JSON и Redis."""
    
    id: str
    name: str
    description: str
    total_cards: int
    downloaded: int
    last_synced_at: str
    author_id: str
    author_first_name: str
    author_last_name: str
    author_avatar_url: str

    def to_dict(self) -> dict:
        """Сериализация в словарь (для Redis JSON)."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "total_cards": self.total_cards,
            "downloaded": self.downloaded,
            "last_synced_at": self.last_synced_at,
            "author_id": self.author_id,
            "author_first_name": self.author_first_name,
            "author_last_name": self.author_last_name,
            "author_avatar_url": self.author_avatar_url,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PublicDeckPreview":
        """Десериализация из словаря."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            total_cards=data.get("total_cards", 0),
            downloaded=data.get("downloaded", 0),
            last_synced_at=data.get("last_synced_at"),
            author_id=data.get("author_id", ""),
            author_first_name=data.get("author_first_name", ""),
            author_last_name=data.get("author_last_name", ""),
            author_avatar_url=data.get("author_avatar_url", ""),
        )

    @classmethod
    def from_cloud_deck(cls, deck: CloudDeck, author: GetProfileUserOutput) -> "PublicDeckPreview":
        """Создание из доменной сущности CloudDeck and User."""

        return cls(
            id=str(deck.id),
            name=deck.name,
            description=deck.description,
            total_cards=deck.total_cards,
            downloaded=deck.downloaded,
            last_synced_at=deck.last_synced_at.isoformat(),
            author_id=str(deck.author_id),
            author_first_name=author.first_name,
            author_last_name=author.last_name,
            author_avatar_url=author.avatar_url,
        )

    def to_json(self) -> str:
        """Сериализация в JSON-строку."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "PublicDeckPreview":
        """Десериализация из JSON-строки."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass(frozen=True, slots=True)
class PublicDecksListOutput:
    """
    Обертка для хранения всего списка публичных колод в одном ключе Redis.
    """
    decks: List[PublicDeckPreview] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Сериализация всего списка в словарь."""
        return {
            "decks": [deck.to_dict() for deck in self.decks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PublicDecksListOutput":
        """Десериализация словаря обратно в список."""
        decks_data = data.get("decks", [])
        decks = [PublicDeckPreview.from_dict(d) for d in decks_data]
        return cls(
            decks=decks,
        )


    @classmethod
    def from_decks_with_authors(cls, decks_authors_list: List[Tuple[CloudDeck, GetProfileUserOutput]]) -> "PublicDecksListOutput":
        """
        Создание списка из доменных сущностей.
        """
        preview_decks = []
        for deck, author in decks_authors_list:
            preview_decks.append(PublicDeckPreview.from_cloud_deck(deck=deck, author=author))
        
        return cls(
            decks=preview_decks,
        )

    def to_json(self) -> str:
        """Сериализация всего списка в JSON-строку."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "PublicDecksListOutput":
        """Десериализация JSON-строки в список."""
        data = json.loads(json_str)
        return cls.from_dict(data)