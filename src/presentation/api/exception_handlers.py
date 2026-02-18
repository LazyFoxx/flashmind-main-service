import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.application.exceptions import (
    CardAlreadyExistsError,
    CardNotExistsError,
    DeckAlreadyExistsError,
    DeckNotExistsError,
    InvalidTokenError,
)

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


async def deck_not_exist(request: Request, exc: DeckNotExistsError) -> JSONResponse:
    logger.warning(
        f"У пользователя нет такой колоды",
        deck_id=str(exc.deck_id),
        user_id=str(exc.user_id),
    )
    return JSONResponse(
        status_code=404,
        content={
            "message": f"У пользователя нет такой колоды",
        },
    )


async def card_exist(request: Request, exc: CardAlreadyExistsError) -> JSONResponse:
    logger.warning(
        "Карточка с таким front уже существует",
        front=exc.front,
        deck_id=str(exc.deck_id),
    )
    return JSONResponse(
        status_code=409,
        content={
            "message": f"Карточка с таким front уже существует в этой колоде",
        },
    )


async def card_not_exist(request: Request, exc: CardNotExistsError) -> JSONResponse:
    logger.warning(
        f"Карточка не найдена",
        card_id=str(exc.card_id),
    )
    return JSONResponse(
        status_code=404,
        content={
            "message": f"Карточка не найдена",
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Единая регистрация всех обработчиков ошибок."""
    app.add_exception_handler(InvalidTokenError, invalid_token)  # type: ignore[arg-type]
    app.add_exception_handler(DeckAlreadyExistsError, deck_exist)  # type: ignore[arg-type]
    app.add_exception_handler(CardAlreadyExistsError, card_exist)  # type: ignore[arg-type]
    app.add_exception_handler(DeckNotExistsError, deck_not_exist)  # type: ignore[arg-type]
    app.add_exception_handler(CardNotExistsError, card_not_exist)  # type: ignore[arg-type]
