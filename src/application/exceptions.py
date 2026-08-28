
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
        
class CloudDeckNotExistsError(Exception):
    def __init__(self, message: str):
        self.message = message


class UserIsNotAuthor(Exception):
    def __init__(self, user_id: UUID, message: str):
        self.user_id = user_id
        self.message = message


class CardAlreadyExistsError(Exception):
    def __init__(self, title: str, deck_id: UUID):
        self.title = title
        self.deck_id = deck_id


class CardNotInLearningError(Exception):
    def __init__(self, card_id: UUID):
        self.card_id = card_id


class InvalidTokenError(ApplicationError):
    pass


class UserNotFoundError(ApplicationError):
    def __init__(self, user_id: str):
        self.user_id = user_id


class InsufficientReviewsError(ApplicationError):
    """Недостаточно повторов для AI-анализа"""
    def __init__(self, total_reviews: int, remaining_reviews: int):
        self.total_reviews = total_reviews
        self.remaining_reviews = remaining_reviews


class DeckImportFromOwnAuthorError(ApplicationError):
    """Пользователь пытается импортировать свою же колоду"""
    def __init__(self, deck_id: UUID, user_id: UUID):
        self.deck_id = deck_id
        self.user_id = user_id
