import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.application.exceptions import DeckAlreadyExistsError, InvalidTokenError

logger = structlog.get_logger()


async def invalid_token(request: Request, exc: InvalidTokenError) -> JSONResponse:
    logger.warning("Неверный токен", error=str(exc))
    return JSONResponse(
        status_code=401,
        headers={"WWW-Authenticate": "Bearer"},
        content={
            "message": f"Неверный токен",
        },
    )


async def deck_exist(request: Request, exc: DeckAlreadyExistsError) -> JSONResponse:
    logger.warning(
        "Колода с таким названием уже существует",
        deck_name=exc.name,
        user_id=str(exc.user_id),
    )
    return JSONResponse(
        status_code=409,
        content={
            "message": f"Колода с таким названием уже существует",
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Единая регистрация всех обработчиков ошибок."""
    app.add_exception_handler(InvalidTokenError, invalid_token)  # type: ignore[arg-type]
    app.add_exception_handler(DeckAlreadyExistsError, deck_exist)  # type: ignore[arg-type]
