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
            container=container,  # передаем контейнер
            callback_key=USER_REGISTERED,  # передаем ключ DI
        )
    )

    yield
    # shutdown
    await container.close()



app = FastAPI(
    lifespan=lifespan,
    version="1.2.8",
       # title="",
    description="""
    1.2.8
    **Новая функция: Поддержка пользовательских таймзонов**
    
    Все даты и времена в ответах API теперь учитывают часовой пояс пользователя.
    
    Обязательный заголовок для всех запросов:
        - `X-Timezone`: IANA таймзона (например: "Europe/Moscow", "America/New_York", "Asia/Tokyo")
        - Если заголовок не передан или невалиден — используется UTC по умолчанию
        - Валидация через `zoneinfo.ZoneInfo()` — автоматически проверяет корректность
    
    Затронутые эндпоинты:
        - `GET /users/profile` — статистика (daily_review_counts, review_series) в таймзоне пользователя
        - `GET /stats/stats` — вся статистика (forecast, review_count, review_time, hourly_breakdown) в таймзоне пользователя
        - `GET /study/study-cards` — due cards учитывают cutoff time пользователя
        - `POST /study/review-card` — лог ревью сохраняется в таймзоне пользователя
        - `GET /decks/user-decks` — сортировка и фильтрация по updated_at в таймзоне пользователя
        - `POST /ai/analyze-study-stat` — анализ в контексте таймзоны пользователя
    
    Технические детали:
        - `review_datetime` в БД хранится с timezone (PostgreSQL `timestamp with time zone`)
        - `next_due` (due time карточек) хранится с timezone
        - `next_review_datetime` хранится с timezone
        - Cutoff time (rollover hour = 3:00) применяется в таймзоне пользователя
        - Timezone синхронизируется: если заголовок отличается от сохранённого — обновляется в БД
    
    Примеры заголовков:
        - `X-Timezone: Europe/Moscow`
        - `X-Timezone: America/Los_Angeles`
        - `X-Timezone: Asia/Tokyo`
        - `X-Timezone: UTC`
    
    1.2.7
    Новый эндпоинт:
    - AI-анализ статистики обучения
        /api/v1/flashmind/ai/analyze-study-stat
        Анализ статистики обучения пользователя с помощью AI (DeepSeek).
        Проверяет количество повторов, анализирует статистику и возвращает:
        - AIStudyAnalysisResult: общий анализ с проблемами, рекомендациями, целями
        - insights: список инсайтов по карточкам
        - problem_areas: проблемные области
        - recommendations: рекомендации по улучшению
        - goals: цели обучения
        
        Новая ошибка 422 INSUFFICIENT_REVIEWS:
        Возвращается когда недостаточно повторов для AI-анализа
        Пример ответа:
            {
            "error": "INSUFFICIENT_REVIEWS",
            "message": "Недостаточно повторов для AI-анализа. У вас X из 100. Необходимо еще Y.",
            "total_reviews": X,
            "remaining_reviews": Y
            }
        
        Изменения:
        - Исправлен график карточек (get_card_types_stats)
            Теперь учитывается deck_id — до этого возвращал повторы по рейтингам без привязки к колоде
        - Исправлен график прогноза
            Теперь учитываются повторы на сегодня
        - Изменены описания типов карт в get_card_types_stats
            С русских на английские: 'new', 'in_learning', 'learned', 'suspended'
    
    1.2.6
    - Добавлены responses в эндпоинты с ошибкой 410 ( облачная колода не найдена)
    
    1.2.5
    Исправлены ошибки обработки исключений в облачных колодах:
     
     
     - Добавлен error_code в ответ при удалении облачной колоды автором
         CloudDeckNotExistsError теперь возвращает 410 Gone с error_code "CLOUD_DECK_NOT_EXIST"
         Пример ответа:
          {
              "error_code": "CLOUD_DECK_NOT_EXIST",
              "message": "Автор удалил эту колоду из общего облака"
          }
          
    Внутренние фиксы: 
     - Добавлена try/except обёртка в enable_sharing/use_case.py
         Теперь все известные исключения (DeckNotExistsError, UserNotFoundError,
         UserIsNotAuthor, CloudDeckNotExistsError) правильно пробрасываются в handler'ы
     - Добавлена try/except обёртка в import_deck/use_case.py
         Исправлено корректное возвращение 400/410 при ошибках импорта
     - Исправлен dead code в delete_cloud_deck/use_case.py
         Удалён неиспользуемый код после return None
     - Добавлена try/except обёртка в sync_cards_to_cloud/use_case.py
         Добавлено логирование ошибок при синхронизации карточек
     - Исправлен баг с cloud_deck_id в enable_sharing
         cloud_deck_id теперь сохраняется до использования
     - Удалён бесполезный finally блок из get_public_decks/use_case.py

    1.2.4
    Добавил 1 новый эндпонт:
    - Эндпоинст статистики пользователя
        /api/v1/flashmind/stats/stats
    
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
