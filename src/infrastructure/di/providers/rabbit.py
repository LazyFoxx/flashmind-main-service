from typing import Awaitable, Callable

from aio_pika import IncomingMessage
from dishka import Provider, Scope, provide
from dishka.entities.key import DependencyKey

from src.application.use_cases.users.create_user_profile.use_case import (
    CreateUserProfileUseCase,
)
from src.core.settings.rabbit import RabbitSettings
from src.infrastructure.rabbit import (
    RabbitConnection,
    RabbitConsumer,
    process_user_registered,
)

USER_REGISTERED = DependencyKey(Callable, "user_registered")


class RabbitProvider(Provider):
    @provide(scope=Scope.APP)
    async def rabbit_connection(self, settings: RabbitSettings) -> RabbitConnection:
        conn = RabbitConnection(settings)
        await conn.connect()  # подключаемся один раз на всё приложение
        await conn.ensure_topology()  # настраиваем топологию
        return conn

    @provide(scope=Scope.APP)
    async def consumer(self, conn: RabbitConnection) -> RabbitConsumer:
        return RabbitConsumer(conn)

    @provide(scope=Scope.REQUEST, provides=USER_REGISTERED)
    def user_registered_callback(
        self,
        use_case: CreateUserProfileUseCase,
    ) -> Callable[[IncomingMessage], Awaitable[None]]:
        async def callback(message: IncomingMessage) -> None:
            await process_user_registered(message, use_case)

        return callback
