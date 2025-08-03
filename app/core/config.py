# app/core/config.py

from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings
from fastapi_mail import ConnectionConfig
from fastapi.templating import Jinja2Templates

# Template loader
templates = Jinja2Templates(directory=str(
    Path(__file__).parent.parent / "templates" / "email"))

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


class Settings(BaseSettings):
    FRONTEND_DEV_URL: Optional[str] = None
    FRONTEND_PROD_URL: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    JWT_SECRET_KEY: Optional[str] = None
    JWT_EXPIRATION_TIME: int = 6 * 60 * 60  # default to 6 hours if not set

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    SUPPORT_EMAIL: Optional[str] = None
    APP_PASSWORD: Optional[str] = None

    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()


mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.SUPPORT_EMAIL,  # type: ignore
    MAIL_PASSWORD=settings.APP_PASSWORD,  # type: ignore
    MAIL_FROM=settings.SUPPORT_EMAIL,  # type: ignore
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=TEMPLATES_DIR
)
