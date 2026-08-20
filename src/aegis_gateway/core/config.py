from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "Aegis-LLM-Gateway"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API Keys
    OPENAI_API_KEY: str = Field(default="sk-dummy-openai-key")
    GEMINI_API_KEY: str = Field(default="dummy-gemini-key")

    # Guardrails flags
    ENABLE_PII_MASKING: bool = True
    ENABLE_JAILBREAK_DETECTION: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./aegis_gateway.db"


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance singleton des paramètres."""
    return Settings()