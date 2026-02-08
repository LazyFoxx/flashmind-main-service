from pydantic import BaseModel


class EmailAlreadyExistsResponse(BaseModel):
    error: str = "EmailAlreadyExists"
    message: str
    email: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "EmailAlreadyExists",
                "message": "Email уже используется: user@example.com",
                "email": "user@example.com",
            }
        }
    }


class CooldownEmailResponse(BaseModel):
    error: str = "CooldownEmail"
    message: str
    remaining_seconds: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "RateLimitExceeded",
                "message": "Отправьте код позже: 43 секунды",
                "remaining_seconds": "43",
            }
        }
    }


class RateLimitExceededResponse(BaseModel):
    error: str = "RateLimitExceeded"
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "RateLimitExceeded",
                "message": "Слишком много попыток, повторите позже",
            }
        }
    }


class LimitCodeAttemptsResponse(BaseModel):
    error: str = "LimitCodeAttempt"
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "LimitCodeAttempt",
                "message": "Все попытки исчерпаны, начните регистрацию заново или запросите новый код",
            }
        }
    }


class CodeAttemptResponse(BaseModel):
    error: str = "CodeAttempt"
    message: str
    attempts: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "CodeAttempt",
                "message": "Неверный код, осталось попыток: 3",
                "attempts": 3,
            }
        }
    }


class RequestExpiredResponse(BaseModel):
    error: str = "RequestExpired"
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "RequestExpired",
                "message": "Запрос истек, начните попытку заново",
            }
        }
    }


class InvalideCredentialResponse(BaseModel):
    error: str = "InvalideCredential"
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "InvalideCredential",
                "message": "Неверный логин или пароль",
            }
        }
    }
