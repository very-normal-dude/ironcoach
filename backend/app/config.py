from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SQLite works out of the box. Later, switch to PostgreSQL by changing
    # DATABASE_URL in your .env, e.g. postgresql+psycopg://user:pass@localhost/ironcoach
    database_url: str = "sqlite:///./ironcoach.db"
    secret_key: str = "dev-only-change-me-use-a-long-random-string-in-env"
    access_token_expire_minutes: int = 60 * 24  # 1 day
    llm_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
