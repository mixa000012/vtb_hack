import secrets
from datetime import timedelta
from typing import Any
from typing import Dict

from pydantic import BaseSettings
from pydantic import PostgresDsn
from pydantic import validator


class Settings(BaseSettings):
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    PROJECT_NAME: str = "Chatroom"

    PG_SERVER: str = "localhost"
    PG_PORT: int = 5432
    PG_USER: str = "postgres"
    PG_PASSWORD: str = "postgres"
    PG_DB: str = "postgres"
    PG_DATABASE_URI: PostgresDsn | None = None
    PG_POOL_MAX_SIZE: int = 3
    PG_POOL_RECYCLE: int = 1200
    PG_MAX_OVERFLOW: int = 2
    ACCESS_TOKEN_EXPIRE: int = 30

    SECRET_KEY_: str = "secret_key"
    ALGORITHM: str = "HS256"
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    access_token_ttl: timedelta = None
    refresh_token_ttl: timedelta = None

    @validator("PG_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: Dict[str, Any]) -> Any:
        print(values)
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("PG_USER"),
            password=values.get("PG_PASSWORD"),
            host=values.get("PG_SERVER"),
            port=str(values.get("PG_PORT")),
            path=f"/{values.get('PG_DB') or ''}",
        )

    class Config:
        case_sensitive = True
        env_file = "etc/config.env"


settings = Settings()
