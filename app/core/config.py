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
    SQLALCHEMY_DATABASE_URI: Union[str, None] = "sqlite:///./gst_compliance.db"

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, any]) -> str:
        host = values.get("POSTGRES_SERVER")
        # DETECT RENDER INTERNAL URL (UNREACHABLE LOCALLY)
        if host and "dpg-" in host and "render.com" not in host:
            print("WARNING: Detected Render INTERNAL Hostname. This is unreachable locally.")
            print("Falling back to SQLite for local testing.")
            return "sqlite:///./gst_compliance.db"

        # Fallback to SQLite if no Postgres env vars are set (or explicitly requested)
        if host == "localhost" and values.get("POSTGRES_USER") == "postgres":
             # If using default env vars, check if we want to fallback to sqlite easily
             pass

        try:
            return PostgresDsn.build(
                scheme="postgresql",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=host,
                path=f"{values.get('POSTGRES_DB') or ''}",
            ).unicode_string()
        except:
             # Fallback to SQLite
             return "sqlite:///./gst_compliance.db"

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

    # GOOGLE AUTH
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
