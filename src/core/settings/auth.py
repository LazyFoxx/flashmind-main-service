from functools import cached_property

from authlib.jose import JsonWebToken
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    jwks_url: str
    issuer: str
    algorithm: str = "RS256"
    jwks_cache_ttl_seconds: int = 3600

    @cached_property
    def jwt(self) -> JsonWebToken:
        return JsonWebToken([self.algorithm])

    model_config = SettingsConfigDict(
        env_prefix="AUTH_", case_sensitive=False, extra="ignore"
    )
