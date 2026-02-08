from redis.asyncio import Redis, from_url

from src.core.settings import RedisSettings


async def create_redis_client(settings: RedisSettings) -> Redis:
    client = from_url(
        settings.get_url(),
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
    )

    try:
        await client.ping()
    except Exception:
        await client.aclose()
        raise

    return client
