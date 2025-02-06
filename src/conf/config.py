from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class loads environment variables and default values required
    for database connections, authentication, email services, and
    cloud storage configurations.

    Attributes:
        DB_URL (str): Database connection URL.
        JWT_SECRET (str): Secret key for JWT authentication.
        JWT_ALGORITHM (str): Algorithm used for JWT encoding/decoding.
        JWT_EXPIRATION_MINUTES (int): JWT expiration time in minutes.

        MAIL_USERNAME (str): Username for email service.
        MAIL_PASSWORD (str): Password for email service.
        MAIL_FROM (EmailStr): Sender email address.
        MAIL_PORT (int): Email server port.
        MAIL_SERVER (str): SMTP server address.
        MAIL_FROM_NAME (str): Display name for outgoing emails.
        MAIL_STARTTLS (bool): Enable STARTTLS for email encryption.
        MAIL_SSL_TLS (bool): Enable SSL/TLS for email encryption.
        USE_CREDENTIALS (bool): Whether to use authentication credentials for email.
        VALIDATE_CERTS (bool): Whether to validate SSL certificates for email.

        CLD_NAME (str): Cloudinary storage provider name.
        CLD_API_KEY (int): API key for Cloudinary storage.
        CLD_API_SECRET (str): API secret for Cloudinary storage.

        model_config (ConfigDict): Pydantic configuration for environment variable management.
    """

    DB_URL: str = "postgresql+asyncpg://postgres:1234@postgres:5432/postgres"
    JWT_SECRET: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 5

    MAIL_USERNAME: str = "example@com.ua"
    MAIL_PASSWORD: str = "1234"
    MAIL_FROM: EmailStr = "example@com.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "fastapi-app"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str = "abcdefghi"
    CLD_API_KEY: int = 123456789012345
    CLD_API_SECRET: str = "a0cde0GhIJk-lMnopQRSTUVWXyz"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
"""
Global instance of the Settings class.

Loads configuration values from environment variables and provides
a single access point for configuration throughout the application.
"""
