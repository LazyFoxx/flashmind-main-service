from dataclasses import dataclass, replace
from typing import Optional
from uuid import UUID


@dataclass(slots=True, frozen=True)
class User:
    """
    Доменная сущность пользователя.
    """

    id: UUID
    first_name: str
    last_name: str
    avatar_key: str
    bio: Optional[str] = None
    timezone: str = "UTC"

    def with_timezone(self, timezone: str) -> "User":
        """Возвращает копию User с новым timezone (для frozen dataclass)."""
        return replace(self, timezone=timezone)
