import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Auth Service"
    environment: str = os.getenv("ENVIRONMENT")

    database_url: str = os.getenv("DATABASE_URL")

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    access_token_expire_minutes: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


settings = Settings()
