import httpx
from authlib.jose import JsonWebKey

from src.application.interfaces import JWKSCache
from src.core.settings import AuthSettings


class JWKSClient:
    def __init__(self, cache: JWKSCache, settings: AuthSettings):
        self.url = settings.jwks_url
        self.ttl = settings.jwks_cache_ttl_seconds
        self.cache = cache
        self._memory: dict[str, JsonWebKey] = {}

    async def get_key(self, kid: str) -> JsonWebKey:
        # L1 cache
        if kid in self._memory:
            return self._memory[kid]

        # L2 cache
        key = await self.cache.get(kid)
        if key:
            self._memory[kid] = key
            return key

        # JWKS endpoint
        async with httpx.AsyncClient() as client:
            jwks = (await client.get(self.url)).json()

        for k in jwks["keys"]:
            parsed = JsonWebKey.import_key(k)
            self._memory[k["kid"]] = parsed
            await self.cache.set(k["kid"], parsed, self.ttl)

        return self._memory.get(kid)
