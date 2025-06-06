from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
import secrets
from typing import List, Union
from pydantic import AnyHttpUrl, validator
# Load environment variables from .env file
load_dotenv(override=True)

class Settings(BaseSettings):
    # Environment settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Base URL settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3000",     
        "http://localhost:5173",     
        "http://localhost:8080",     
        "http://localhost:4200",     
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200",
        "http://100.64.0.2:3000",    # Add your actual frontend IP
        "http://100.64.0.3:3000",    # Add your actual frontend IP
        "http://100.64.0.4:3000",    # Add your actual frontend IP
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # أضف المتغير ده عشان ما يسببش مشكلة
    REACT_APP_BASE_URL: AnyHttpUrl  # أو str لو مش عايز تتحقق انه URL

    class Config:
        env_file = ".env"
        extra = "forbid"  # يمنع المتغيرات الغير معرفة (لو عندك مشاكل، خليها "ignore")

    
    # Database settings
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "Zyad@1755")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3307")
    DB_NAME: str = os.getenv("DB_NAME", "gymqrs_qrsdb")
    
    # SSL settings
    SSL_CERTIFICATE: str = os.getenv("SSL_CERTIFICATE", "cert.pem")
    SSL_KEY: str = os.getenv("SSL_KEY", "key.pem")
    FORCE_HTTPS: bool = os.getenv("FORCE_HTTPS", "True").lower() == "true"
    DOMAIN: str = os.getenv("DOMAIN", "localhost")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Security settings
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_MAX_LENGTH: int = 128
    PASSWORD_REGEX: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = 15
    
    # OTP settings
    OTP_EXPIRATION_MINUTES: int = 5
    OTP_LENGTH: int = 6
    OTP_MAX_ATTEMPTS: int = 3
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    LOGIN_RATE_LIMIT: int = 5
    SIGNUP_RATE_LIMIT: int = 5
    
    # CORS settings
    CORS_ORIGINS: List[str] = BACKEND_CORS_ORIGINS
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Session settings
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    
    # SMS Settings
    # TWILIO_ACCOUNT_SID: str = ""
    # TWILIO_AUTH_TOKEN: str = ""
    # TWILIO_PHONE_NUMBER: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 