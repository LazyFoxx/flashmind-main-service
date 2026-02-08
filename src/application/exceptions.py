class ApplicationError(Exception):
    """Базовый класс для application ошибок"""


class UserAlreadyExistsError(ApplicationError):
    """Профиль пользователя уже занят"""

    pass


class InvalidTokenError(ApplicationError):
    pass


class UserNotFoundError(ApplicationError):
    pass
