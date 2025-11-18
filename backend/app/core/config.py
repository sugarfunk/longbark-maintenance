from typing import Any, Dict, List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, validator
import secrets


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    PROJECT_NAME: str = "LongBark Hosting Manager"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[PostgresDsn] = None

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379/0"

    # Admin User
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # NTFY Configuration
    NTFY_ENABLED: bool = True
    NTFY_SERVER_URL: str = "https://ntfy.sh"
    NTFY_DEFAULT_TOPIC: str = "longbark-alerts"
    NTFY_PRIORITY: str = "default"
    NTFY_TOPIC_UPTIME: Optional[str] = None
    NTFY_TOPIC_SSL: Optional[str] = None
    NTFY_TOPIC_PERFORMANCE: Optional[str] = None
    NTFY_TOPIC_SEO: Optional[str] = None
    NTFY_TOPIC_WORDPRESS: Optional[str] = None

    # Invoice Ninja Configuration
    INVOICE_NINJA_ENABLED: bool = False
    INVOICE_NINJA_URL: Optional[str] = None
    INVOICE_NINJA_API_TOKEN: Optional[str] = None
    INVOICE_NINJA_API_VERSION: str = "v5"

    # Google Search Console
    GSC_ENABLED: bool = False
    GSC_CREDENTIALS_FILE: Optional[str] = None

    # Monitoring Configuration
    DEFAULT_CHECK_INTERVAL: int = 300  # 5 minutes
    UPTIME_TIMEOUT: int = 30
    SSL_WARNING_DAYS: int = 30
    PERFORMANCE_THRESHOLD: int = 3000  # milliseconds
    BROKEN_LINK_MAX_THREADS: int = 10

    # Screenshot Configuration
    SCREENSHOT_ENABLED: bool = True
    SCREENSHOT_WIDTH: int = 1920
    SCREENSHOT_HEIGHT: int = 1080

    # Report Configuration
    REPORT_LOGO_URL: Optional[str] = None
    REPORT_COMPANY_NAME: str = "LongBark Hosting"
    REPORT_SUPPORT_EMAIL: Optional[EmailStr] = None

    # URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
