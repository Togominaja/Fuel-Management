from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fleet Command MVP"
    database_url: str = "sqlite:///./fleet_mvp.db"
    secret_key: str = "replace-with-a-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    bootstrap_admin_email: str = "sbravatti.nelson@gmail.com"
    bootstrap_admin_password: str = "ChangeMe123!"
    seed_demo_data: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
