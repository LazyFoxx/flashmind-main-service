from uuid import UUID


class ApplicationError(Exception):
    """Базовый класс для application ошибок"""


class UserAlreadyExistsError(ApplicationError):
    """Профиль пользователя уже занят"""

    pass


class CardNotExistsError(Exception):
    def __init__(self, card_id: UUID):
        self.card_id = card_id


class DeckAlreadyExistsError(Exception):
    def __init__(self, name: str, user_id: UUID):
        self.name = name
        self.user_id = user_id


class DeckNotExistsError(Exception):
    def __init__(self, deck_id: UUID, user_id: UUID):
        self.deck_id = deck_id
        self.user_id = user_id


class CardAlreadyExistsError(Exception):
    def __init__(self, front: str, deck_id: UUID):
        self.front = front
        self.deck_id = deck_id


class InvalidTokenError(ApplicationError):
    pass


class UserNotFoundError(ApplicationError):
    def __init__(self, user_id: str):
        self.user_id = user_id
