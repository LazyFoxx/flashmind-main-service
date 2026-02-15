import json
from typing import Awaitable, Callable

import structlog
from aio_pika import IncomingMessage
from dishka import AsyncContainer, DependencyKey

from src.application.use_cases.users.create_user_profile.use_case import (
    CreateUserProfileUseCase,
)

from .connection import RabbitConnection

logger = structlog.get_logger(__name__)


class RabbitConsumer:
    def __init__(self, connection: RabbitConnection):
        self._connection = connection
        self.logger = structlog.get_logger(__name__)
        self._running = False

    async def start_consuming(
        self,
        queue_name: str,
        container: AsyncContainer,  # корневой контейнер (APP scope)
        callback_key: DependencyKey,
    ) -> None:
        """
        Для КАЖДОГО сообщения создаём отдельный REQUEST scope.
        """
        try:
            channel = self._connection.channel
            queue = await channel.get_queue(queue_name)

            self._running = True

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    if not self._running:
                        break

                    try:
                        # ← Вот здесь правильный вход в REQUEST scope
                        async with container() as request_scope:
                            callback: Callable[[IncomingMessage], Awaitable[None]] = (
                                await request_scope.get(callback_key)
                            )
                            await callback(message)

                    except Exception as e:
                        self.logger.error(
                            "Ошибка обработки сообщения",
                            error=str(e),
                            exc_info=True,
                        )
                        await message.nack(requeue=True)

            self.logger.info(f"Consumer stopped for queue {queue_name}")

        except Exception as e:
            self.logger.error("Ошибка запуска consumer", error=str(e), exc_info=True)
            raise


# Callback: Обрабатывает сообщение, извлекает user_id и вызывает Use Case
async def process_user_registered(
    message: IncomingMessage, use_case: CreateUserProfileUseCase
) -> None:
    async with message.process(ignore_processed=True):  # Авто-ack/nack
        try:
            payload = json.loads(message.body.decode())
            user_id = payload.get(
                "user_id"
            )  # Предполагаем, что в payload есть {"user_id": 123}

            if not user_id:
                raise ValueError("No user_id in payload")

            logger.info(
                "Получено сообщение с user_id", user_id=user_id, payload=payload
            )

            # Вызываем Use Case для обработки
            await use_case.execute(user_id)

            await message.ack()  # Явный ack после успеха

        except Exception as e:
            logger.error("Ошибка обработки сообщения", error=str(e), exc_info=True)
            await message.nack(requeue=True)
