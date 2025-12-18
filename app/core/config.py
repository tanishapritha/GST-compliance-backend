import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, PostgresDsn, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "GST Compliance Copilot"
    API_V1_STR: str = "/api/v1"
    
    # POSTGRES
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "gst_compliance_db")
    SQLALCHEMY_DATABASE_URI: Union[str, None] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, any]) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        ).unicode_string()

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeywhichshouldbechanged")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # REDIS
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    # UPLOAD
    UPLOAD_FOLDER: str = os.path.join(os.getcwd(), "uploads")

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
