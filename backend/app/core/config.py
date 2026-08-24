from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- App metadata ---
    APP_NAME: str = "AgentOps"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- Database settings ---
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Security / JWT ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- LLM Providers ---
    DEEPSEEK_API_KEY: str
    OPENAI_API_KEY: str  # used for embeddings only


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
