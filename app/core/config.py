from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "llm-text-score-service"
    APP_ENV: str = "dev"

    ENABLE_LLM: bool = False
    LLM_API_KEY: str | None = None
    LLM_TIMEOUT_SECONDS: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

