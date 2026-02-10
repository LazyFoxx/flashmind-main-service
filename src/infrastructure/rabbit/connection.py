from types import TracebackType
from typing import Optional

import aio_pika
import structlog
from aio_pika import (
    ExchangeType,
    RobustChannel,
    RobustConnection,
)

from src.core.settings import RabbitSettings


class RabbitConnection:
    def __init__(self, settings: RabbitSettings):
        self.settings = settings
        self._connection: RobustConnection | None = None
        self._channel: RobustChannel | None = None
        self._topology_setup_done = (
            False  # Флаг, чтобы не настраивать топологию повторно
        )
        self.logger = structlog.get_logger(__name__)

    async def connect(self) -> None:
        """
        Подключается к RabbitMQ, создаёт канал, устанавливает QoS
        и настраивает топологию (exchange, queues, bindings) один раз.
        """
        # Проверяем, не подключены ли уже (idempotent)
        if self._connection is not None:
            return

        # Подключаемся к RabbitMQ
        self._connection = await aio_pika.connect_robust(self.settings.get_url())

        # Создаём канал
        self._channel = await self._connection.channel()

        # Устанавливаем QoS
        await self._channel.set_qos(prefetch_count=10)

        # Настраиваем топологию RabbitMQ (exchange, queues, bindings)
        await self.ensure_topology()

    async def ensure_topology(self) -> None:
        """
        Настраивает структуру RabbitMQ: exchange, очереди и биндинги.
        Это безопасно вызывать повторно (idempotent), используем флаг,
        чтобы избежать ненужных вызовов.
        """
        if self._topology_setup_done:
            return  # Уже настроено, пропускаем

        if not self._channel:
            self.logger.error("Канал не инициализирован")
            raise RuntimeError("Channel not initialized")

        # ─── 1. Объявляем exchange ──────────────────────────────────────────
        # Имя: "events"
        # Тип: DIRECT (по умолчанию в aio_pika, но указываем явно для ясности)
        # Durable: True — сохраняется при рестарте RabbitMQ
        # Auto-delete: False — не удаляется автоматически
        events_exchange = await self._channel.declare_exchange(
            name="events",
            type=ExchangeType.DIRECT,  # Прямой роутинг по ключу
            durable=True,
            auto_delete=False,
        )

        # ─── 2. Объявляем очереди ───────────────────────────────────────────
        # Имя: "register_user"
        # Durable: True — сохраняется при рестарте
        # Exclusive: False — не привязана к одному соединению
        # Auto-delete: False — не удаляется автоматически
        reg_queue = await self._channel.declare_queue(
            name="register_user",
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        # ─── 3. Привязываем очередь к exchange (binding) ────────────────────
        # все сообщения с routing_key="user.registered"
        # будут попадать в очередь "register_user"
        await reg_queue.bind(
            exchange=events_exchange,
            routing_key="user.registered",
        )

        # Если нужно больше очередей, добавьте здесь:
        # email_queue = await self._channel.declare_queue(
        #     name="email_notifications",
        #     durable=True,
        #     exclusive=False,
        #     auto_delete=False,
        # )
        # await email_queue.bind(
        #     exchange=events_exchange,
        #     routing_key="user.delete",  # Другой routing key
        # )

        # Флаг, что настройка завершена
        self._topology_setup_done = True
        self.logger.info(
            "RabbitMQ (exchanges, queues, bindings) инициализированны успешно"
        )

    async def close(self) -> None:
        """
        Закрывает канал и соединение.
        Сбрасывает флаг топологии для возможного переподключения.
        """
        if self._channel:
            await self._channel.close()
            self._channel = None
        if self._connection:
            await self._connection.close()
            self._connection = None
        self._topology_setup_done = False

    async def __aenter__(self) -> "RabbitConnection":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()

    @property
    def channel(self) -> RobustChannel:
        if not self._channel:
            raise RuntimeError("Rabbit channel is not initialized")
        return self._channel
