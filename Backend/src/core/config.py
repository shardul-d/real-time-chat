from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parents[2]
ENV_PATH: Path = BASE_DIR / ".env"

class EnvironmentVariables(BaseSettings):
    JWT_SECRET: str
    JWT_EXPIRY_IN_HOURS: int
    JWT_ALGORITHM: str
    DATABASE_URL: str
    
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8")


config: EnvironmentVariables = EnvironmentVariables() #pyright: ignore[reportCallIssue]