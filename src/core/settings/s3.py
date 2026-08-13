from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    endpoint_url: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    bucket_name: str

    model_config = SettingsConfigDict(
        env_prefix="S3_", case_sensitive=False, extra="ignore"
    )
