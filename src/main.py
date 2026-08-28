import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.logging.config import setup_logging
from src.core.middleware.logging_middleware import LoggingMiddleware
from src.core.middleware.timezone_middleware import TimezoneMiddleware
from src.core.settings import cors_config
from src.infrastructure.di.container import get_container
from src.infrastructure.di.providers.rabbit import USER_REGISTERED
from src.infrastructure.rabbit import RabbitConsumer
from src.presentation.api.exception_handlers import setup_exception_handlers
from src.presentation.api.routers.root import  api_router_v1

container = get_container()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    setup_logging()

    consumer: RabbitConsumer = await container.get(RabbitConsumer)

    # Запускаем consumer в background task
    asyncio.create_task(
        consumer.start_consuming(
            queue_name="register_user",
            container=container,   # передаем контейнер
            callback_key=USER_REGISTERED,   # передаем ключ DI
          )
       )

    yield
    # shutdown
    await container.close()



app = FastAPI(
    lifespan=lifespan,
    version="2.0.0",
           # title="",
    description="""
        2.0.0 - Глобальная переработка модели карточки и обучения

        ---

       Cards API (/api/v1/flashmind/cards)

       POST /cards — создание карточки
        - CreateCardRequest: front: str → front: Any (JSON), back: str → back: Any (JSON)
        - Добавлено обязательное поле title: str (название карточки)
        - Добавлены hint1: Optional[str], hint2: Optional[str] (подсказки)
        - **title уникально для всей колоды** (была уникальность по front)
        - Response: CardResponse — полный объект карточки

       PUT /cards/{card_id} — частичное обновление карточки (PATCH)
         - UpdateCardRequest: все поля опциональны — передавай только те поля, которые хочешь изменить
         - Если поле не передано (None) — оно не изменяется
         - Пример: чтобы обновить только front, отправь {"front": [...]} без title, back и других полей
         - Добавлена поддержка поля is_suspended: Optional[bool] для отложенных карточек
         - Response: CardResponse — полный объект карточки

       GET /cards — список карточек колоды
        - Response: CardListResponse → cards: List[CardResponse]
        - Убрана пагинация (page, per_page) и сортировка
        - CardLightResponse заменён на CardResponse

       GET /cards/{card_id} — одна карточка с расширенной статистикой
          - **Response изменён**: теперь возвращается CardDetailResponse (вместо CardResponse)
          - CardDetailResponse включает:
            {
              "card": { /* CardResponse — полный объект карточки */ },
              "last_review_datetime": "2024-01-20T15:30:00Z" | null,
              "next_review_datetime": "2024-01-22T10:00:00Z" | null,
              "review_history": [
                {
                  "review_datetime": "2024-01-10T10:00:00Z",
                  "rating": 3,
                  "difficulty": 2.8,
                  "stability": 1.5,
                  "review_duration_ms": 5000
                }
              ]
            }
          - Новые поля:
            - last_review_datetime — дата последнего повтора (ISO 8601)
            - next_review_datetime — дата следующего повтора (ISO 8601)
            - review_history — массив всех ревью карточки с деталями:
              - review_datetime: дата и время ревью
              - rating: оценка (1: Again, 2: Hard, 3: Good, 4: Easy)
              - difficulty: сложность после ревью
              - stability: стабильность после ревью
              - review_duration_ms: длительность ревью в миллисекундах

          ### Пример ответа CardDetailResponse
          {
            "card": {
              "id": "123e4567-e89b-12d3-a456-426614174000",
              "deck_id": "123e4567-e89b-12d3-a456-426614174001",
              "title": "Любимый напиток",
              "front": [{"type": "text", "value": "Любимый Настин напиток"}],
              "back": [{"type": "text", "value": "Тот что с сарахозаменителем"}],
              "hint1": "Подсказка 1",
              "hint2": "Подсказка 2",
              "difficulty": 3.32344,
              "stability": 1.23434,
              "in_learning": false,
              "card_template_id": null,
              "created_at": "2024-01-15T12:00:00Z"
            },
            "last_review_datetime": "2024-01-20T15:30:00Z",
            "next_review_datetime": "2024-01-22T10:00:00Z",
            "review_history": [
              {
                "review_datetime": "2024-01-10T10:00:00Z",
                "rating": 3,
                "difficulty": 2.8,
                "stability": 1.5,
                "review_duration_ms": 5000
              },
              {
                "review_datetime": "2024-01-15T14:00:00Z",
                "rating": 2,
                "difficulty": 3.0,
                "stability": 1.2,
                "review_duration_ms": 8000
              },
              {
                "review_datetime": "2024-01-20T15:30:00Z",
                "rating": 3,
                "difficulty": 3.3,
                "stability": 1.8,
                "review_duration_ms": 6000
              }
            ]
          }

          ### Важно для фронтенда
          1. GET /cards/{card_id} теперь возвращает CardDetailResponse вместо CardResponse
          2. Поле `card` содержит тот же CardResponse как и раньше
          3. `last_review_datetime` и `next_review_datetime` могут быть null (если не было ревью)
          4. `review_history` — массив всех ревью карточки, отсортированный по дате (asc)
          5. Для новых карточек без истории — вернётся пустой массив review_history и null даты

          ---

       Study API (/api/v1/flashmind/study)

       POST /study/new-to-study — перевод карточек в обучение
        - Response изменён: теперь только `cards: List[CardResponse]` (убрано поле `total`)
        - Убрана логика добавления due cards — теперь возвращаются только новые карточки

       POST /study/review-card — повтор карточки
        - Response изменён: теперь всегда возвращает `ReviewDueCardResponse` (убран 204 No Content)
        - Новый ответ:
          {
            "card": { /* CardResponse — полный объект */ },
            "success": true/false
          }
        - success — true если карточку больше не нужно повторять сегодня, false — отправить на повтор

       ### Удалено
       - GET /study/study-cards полностью удалён (GetStudyCardsUseCase удалён)

        ---

       Deck API (/api/v1/flashmind/decks)

       GET /decks/user-decks — колоды пользователя
        - DeckResponse получил новое поле:
          {
            "cards_on_study": [ /* List[CardResponse] — карточки на обучение на сегодня */ ]
          }

       PUT /decks/{deck_id} — обновление колоды
        - Response теперь включает `cards_on_study: List[CardResponse]` (карточки на обучение на сегодня)

        ---

       Cloud Deck API (/api/v1/flashmind/cloud-decks)

       GET /cloud-decks/public — публичные колоды
        - PublicDeckPreviewResponse получил новое поле `description: str`

        ### Удалено
        - GET /cloud-cards/{card_id} полностью удалён (GetCloudCardUseCase удалён)
          - Причина: облачные карточки теперь полностью передаются вместе с превью колоды
            через GET /cloud-decks/public и GET /cloud-decks/{deck_id} — отдельный эндпоинт не нужен

        ---

       Новый универсальный ответ CardResponse (все эндпоинты)

         {
           "id": "uuid",
           "deck_id": "uuid",
           "title": "название карточки",
           "front": [/* JSON: {type: "text", value: "..."} */],
           "back": [/* JSON: {type: "text", value: "..."} */],
           "hint1": "подсказка 1 или null",
           "hint2": "подсказка 2 или null",
           "difficulty": 3.32,
           "stability": 1.23,
           "in_learning": false,
           "card_template_id": "uuid или null",
           "created_at": "2024-01-15T12:00:00Z",
           "is_suspended": false
         }

        ---

       Важно для фронтенда

       1. front и back больше не строки — теперь Any (JSON). Фронтенд должен парсить как объект/массив
       2. title стало обязательным при создании и обновлении карточки
       3. **title уникально для всей колоды** (была уникальность по front)
       4. Появились hint1 и hint2 — дополнительные подсказки
       5. Появилось created_at в ответах
       6. Все карточные эндпоинты возвращают CardResponse — единый формат
       7. Study review-card теперь возвращает success: bool — нужно обрабатывать логику
       8. Study review-card теперь ВСЕГДА возвращает 200 + CardResponse (убран 204 No Content)
       9. Study new-to-study теперь возвращает только cards (убрано поле total)
       10. Deck user-decks теперь включает cards_on_study — список карточек на сегодня
       11. Deck update теперь включает cards_on_study в ответе
       12. Удалён эндпоинт get_study_cards — больше не доступен
       13. Удалён эндпоинт GET /cloud-cards/{card_id} — больше не доступен
       14. **ВАЖНО: Обучение возвращает карточки со всеми полями** — теперь POST /study/review-card возвращает
          обновлённую карточку с актуальными FSRS-параметрами (difficulty, stability, in_learning, due date).
          Фронтенд должен сразу обновлять карточку в списке карточек колоды, а НЕ сбрасывать кеш карточек
          при обучении. Вместо перезагрузки всего списка через GET /cards — замените карточку по ID
          на обновлённую из ответа /study PATCH. Это устраняет лишний запрос и обеспечивает мгновенное обновление UI.
       15. **PUT /cards/{card_id} теперь поддерживает частичное обновление** — все поля опциональны.
          Чтобы обновить только front, отправь {"front": [...]} без title, back и других полей.
          Поля которые не переданы (null/None) остаются без изменений.
       16. **Новое поле is_suspended** — логика отложенной карточки. Когда is_suspended true, карточка
          не появляется в списке due cards для повторения. Поле добавлено во все CardResponse и поддерживается
          в PUT /cards/{card_id}. Фронтенд может использовать это для паузы карточек.

        """,
)


app.add_middleware(LoggingMiddleware)
app.add_middleware(TimezoneMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.origins,
    allow_origin_regex=cors_config.origin_regex,
    allow_credentials=cors_config.allow_credentials,
    allow_methods=cors_config.allow_methods,
    allow_headers=cors_config.allow_headers,
)

setup_dishka(container, app=app)
setup_exception_handlers(app)


app.include_router(api_router_v1)
