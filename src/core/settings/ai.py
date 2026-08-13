
from functools import cached_property

from authlib.jose import JsonWebToken
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    api_key: SecretStr
    model: str
    base_url: str
    
    model_config = SettingsConfigDict(
        env_prefix="AI_", case_sensitive=False, extra="ignore"
      )
