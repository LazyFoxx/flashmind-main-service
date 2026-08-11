import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.application.exceptions import (
    CardAlreadyExistsError,
    CardNotExistsError,
    CardNotInLearningError,
    DeckAlreadyExistsError,
    DeckImportFromOwnAuthorError,
    DeckNotExistsError,
    InsufficientReviewsError,
    InvalidTokenError,
    UserNotFoundError,
    UserIsNotAuthor,
    CloudDeckNotExistsError,
)

logger = structlog.get_logger()

async def user_is_not_author(request: Request, exc: UserIsNotAuthor) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "message": f"{exc.message}",
        },
    )

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
            "message": f"Колода не найдена",
        },
    )

async def cloud_deck_not_exist(request: Request, exc: CloudDeckNotExistsError) -> JSONResponse:
    return JSONResponse(
        status_code=410,
        content={
             "error_code": "CLOUD_DECK_NOT_EXIST",
             "message": f"{exc.message}",
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
            "message": f"Карточка с таким определением уже существует в этой колоде",
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


async def user_not_found(request: Request, exc: UserNotFoundError) -> JSONResponse:
    logger.critical(
        f"Пользователь не найден",
        user_id=str(exc.user_id),
    )
    return JSONResponse(
        status_code=500,
        content={
            "message": f"Пользователь не найден",
        },
    )


async def card_not_in_learning(
    request: Request, exc: CardNotInLearningError
) -> JSONResponse:
    logger.warning(
        f"карточка не добавлена в изучаемые",
        card_id=str(exc.card_id),
    )
    return JSONResponse(
        status_code=422,
        content={
            "message": f"Карточка не добавлена в колоду изучаемые",
        },
    )


async def deck_import_from_own_author(
    request: Request, exc: DeckImportFromOwnAuthorError
) -> JSONResponse:
    logger.warning(
          "Пользователь пытается импортировать свою же колоду",
        deck_id=str(exc.deck_id),
        user_id=str(exc.user_id),
      )
    return JSONResponse(
        status_code=400,
        content={
              "message": "Нельзя импортировать свою же колоду",
          },
      )


async def insufficient_reviews(
    request: Request, exc: InsufficientReviewsError
) -> JSONResponse:
    logger.warning(
        "Недостаточно повторов для AI-анализа",
        total_reviews=exc.total_reviews,
        remaining_reviews=exc.remaining_reviews,
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "INSUFFICIENT_REVIEWS",
            "message": f"Недостаточно повторов для AI-анализа. У вас {exc.total_reviews} из 100. Необходимо еще {exc.remaining_reviews}.",
            "total_reviews": exc.total_reviews,
            "remaining_reviews": exc.remaining_reviews,
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
     """Единая регистрация всех обработчиков ошибок."""
     app.add_exception_handler(InvalidTokenError, invalid_token)     # type: ignore[arg-type]
     app.add_exception_handler(DeckAlreadyExistsError, deck_exist)     # type: ignore[arg-type]
     app.add_exception_handler(CardAlreadyExistsError, card_exist)     # type: ignore[arg-type]
     app.add_exception_handler(DeckNotExistsError, deck_not_exist)     # type: ignore[arg-type]
     app.add_exception_handler(CardNotExistsError, card_not_exist)     # type: ignore[arg-type]
     app.add_exception_handler(UserNotFoundError, user_not_found)     # type: ignore[arg-type]
     app.add_exception_handler(CardNotInLearningError, card_not_in_learning)     # type: ignore[arg-type]
     app.add_exception_handler(DeckImportFromOwnAuthorError, deck_import_from_own_author)     # type: ignore[arg-type]
     app.add_exception_handler(UserIsNotAuthor, user_is_not_author)     # type: ignore[arg-type]
     app.add_exception_handler(CloudDeckNotExistsError, cloud_deck_not_exist)     # type: ignore[arg-type]
     app.add_exception_handler(InsufficientReviewsError, insufficient_reviews)     # type: ignore[arg-type]

