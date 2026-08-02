import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.logging.config import setup_logging
from src.core.middleware.logging_middleware import LoggingMiddleware
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
    version="1.2.2",
    # title="",
    description="""
    Добавилены 3 эндпоинта:
    
    
    
    - Эндпоинт удаления колоды
    Удаляет облачную колоду 
        - Находит облачную колоду по cloud_uuid
        - Удаляет ее физически с сервера и карточки связанные с ней
        - Удаляет все связи других пользователей колоды и делает их локальными
        
        !!! Если автор удалил колоду и нужно пользователю уведомление то использовать флаг
        is_cloud_deck == True and cloud_deck_id == None !!!
        
    - Эндпоинт проверки возможность стать автором пользователю авторской колоды
    Проверяет может ли пользователь стать автором колоды.
           - Находит локальную колоду по deck_id
           - Проверяет изменил ли пользователь описание
           - Проверяет имеет ли 20% своих карточек в колоде
           
    - Эндпоинт чтобы стать автором своей локальной версии авторской колоды
    Отвязывает локальную колоду от чужой облачной и создаёт новую облачную колоду.
        - Проверяет может ли пользователь быть автором колоды
        - Находит текущую локальную колоду по deck_id
        - Создаёт новую облачную колоду с текущим пользователем как автором
        - Отвязывает локальную колоду от оригинальной облачной
        - Привязывает к новой облачной колоде
    
    
    Исправлены баги
    
    - Исправлен баг отвязывания колоды от облака при обновлении
    - Исправлен баг не определения пользовательских карточек
    - Исправлен баг синхранизации удаленных карточек
    - Исправлен баг перезаписывания обновленных карточек пользователя ( которые он обновил авторские карточки )
    """,
)


app.add_middleware(LoggingMiddleware)
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
