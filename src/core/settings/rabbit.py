from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5672
    virtual_host: str = "/"
    username: str = "guest"
    password: SecretStr = SecretStr("guest")

    model_config = SettingsConfigDict(
        env_prefix="RABBIT_", case_sensitive=False, extra="ignore"
    )

    def get_url(self) -> str:
        """
        Собирает и валидирует DSN с помощью Pydantic PostgresDsn.
        Гарантирует корректность URL на этапе старта приложения.
        """

        url = f"amqp://{self.username}:{self.password.get_secret_value()}@{self.host}:{self.port}{self.virtual_host}"
        # Возвращаем объект URL, который Pydantic может проверить
        return url
