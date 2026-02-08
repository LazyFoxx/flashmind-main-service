from typing import List, Optional, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CORSConfig(BaseSettings):
    origins: List[str] = Field(default_factory=list)
    origin_regex: Optional[str] = None
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_prefix="CORS_", case_sensitive=False, extra="ignore"
    )

    @model_validator(mode="after")
    def check_origins(self) -> Self:
        if self.origins and self.origin_regex:
            raise ValueError(
                "Не допустимо оба одновременно: CORS_ORIGINS и CORS_ORIGIN_REGEX"
            )
        return self


cors_config = CORSConfig()
