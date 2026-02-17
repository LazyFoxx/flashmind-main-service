from uuid import UUID


class ApplicationError(Exception):
    """Базовый класс для application ошибок"""


class UserAlreadyExistsError(ApplicationError):
    """Профиль пользователя уже занят"""

    pass


class DeckAlreadyExistsError(Exception):
    def __init__(self, name: str, user_id: UUID):
        self.name = name
        self.user_id = user_id


class InvalidTokenError(ApplicationError):
    pass


class UserNotFoundError(ApplicationError):
    pass
