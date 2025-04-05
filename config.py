"""
Application Configuration Module

This module manages all configuration settings for the application:

Features:
- Database configuration with connection pooling
- User authentication and verification
- Activity and verification logging with partitioning
- Rate limiting and security
- Profile and customer management
- OAuth integration
- Multilingual support
"""

from pydantic import BaseSettings, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import timedelta

class VerificationMethod(str, Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    GOOGLE = "GOOGLE"
    FACEBOOK = "FACEBOOK"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    CUSTOMER = "CUSTOMER"
    SYSTEM = "SYSTEM"

class PartitionInterval(str, Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_SSL_CA: Optional[str] = None
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES: int = 604800  # 1 week

    # Admin settings
    ADMIN_EMAIL: str = "admin@orderme.com"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_FIRST_NAME: str = "Admin"
    ADMIN_LAST_NAME: str = "User"

    # OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None

    # Verification settings
    VERIFICATION_METHODS: List[VerificationMethod] = [VerificationMethod.EMAIL]
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 30
    VERIFICATION_CODE_LENGTH: int = 6
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 10
    MAX_VERIFICATION_ATTEMPTS: int = 3
    VERIFICATION_COOLDOWN_MINUTES: int = 15
    EMAIL_VERIFICATION_TEMPLATE: str = "email_verification.html"
    PHONE_VERIFICATION_TEMPLATE: str = "phone_verification.txt"

    # Rate limiting settings
    RATE_LIMIT_ATTEMPTS: int = 5
    RATE_LIMIT_WINDOW: int = 300
    RATE_LIMIT_BLOCK_DURATION: int = 900

    # Activity logging settings
    ACTIVITY_LOG_ENABLED: bool = True
    ACTIVITY_LOG_RETENTION_DAYS: int = 90
    ACTIVITY_LOG_IP_TRACKING: bool = True
    ACTIVITY_LOG_USER_AGENT_TRACKING: bool = True
    ACTIVITY_LOG_PARTITION_INTERVAL: PartitionInterval = PartitionInterval.MONTH
    ACTIVITY_LOG_CLEANUP_ENABLED: bool = True
    ACTIVITY_LOG_CLEANUP_BATCH_SIZE: int = 1000

    # Verification message logging settings
    VERIFICATION_LOG_RETENTION_DAYS: int = 30
    VERIFICATION_LOG_PARTITION_INTERVAL: PartitionInterval = PartitionInterval.MONTH
    VERIFICATION_LOG_CLEANUP_ENABLED: bool = True
    VERIFICATION_LOG_CLEANUP_BATCH_SIZE: int = 1000

    # User profile settings
    DEFAULT_TIMEZONE: str = "UTC"
    DEFAULT_LANGUAGE: str = "en"
    ALLOWED_LANGUAGES: List[str] = ["en", "es", "fr", "de"]
    PROFILE_PICTURE_MAX_SIZE: int = 5242880  # 5MB
    PROFILE_PICTURE_ALLOWED_TYPES: List[str] = ["image/jpeg", "image/png"]

    # Customer settings
    MAX_CUSTOMERS_PER_PAGE: int = 50
    CUSTOMER_SEARCH_MIN_LENGTH: int = 3
    CUSTOMER_NOTES_MAX_LENGTH: int = 1000

    # Password settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def database_config(self) -> Dict[str, Any]:
        config = {
            "url": self.DATABASE_URL,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE
        }
        if self.is_production and self.DB_SSL_CA:
            config["ssl_ca"] = self.DB_SSL_CA
        return config

    @property
    def jwt_config(self) -> Dict[str, Any]:
        return {
            "secret_key": self.JWT_SECRET_KEY,
            "algorithm": self.JWT_ALGORITHM,
            "access_expires": timedelta(seconds=self.JWT_ACCESS_TOKEN_EXPIRES),
            "refresh_expires": timedelta(seconds=self.JWT_REFRESH_TOKEN_EXPIRES)
        }

    @property
    def verification_config(self) -> Dict[str, Any]:
        return {
            "methods": self.VERIFICATION_METHODS,
            "token_expire_minutes": self.VERIFICATION_TOKEN_EXPIRE_MINUTES,
            "code_length": self.VERIFICATION_CODE_LENGTH,
            "code_expire_minutes": self.VERIFICATION_CODE_EXPIRE_MINUTES,
            "max_attempts": self.MAX_VERIFICATION_ATTEMPTS,
            "cooldown_minutes": self.VERIFICATION_COOLDOWN_MINUTES,
            "email_template": self.EMAIL_VERIFICATION_TEMPLATE,
            "phone_template": self.PHONE_VERIFICATION_TEMPLATE
        }

    @property
    def rate_limit_config(self) -> Dict[str, Any]:
        return {
            "attempts": self.RATE_LIMIT_ATTEMPTS,
            "window": self.RATE_LIMIT_WINDOW,
            "block_duration": self.RATE_LIMIT_BLOCK_DURATION
        }

    @property
    def activity_log_config(self) -> Dict[str, Any]:
        return {
            "enabled": self.ACTIVITY_LOG_ENABLED,
            "retention_days": self.ACTIVITY_LOG_RETENTION_DAYS,
            "ip_tracking": self.ACTIVITY_LOG_IP_TRACKING,
            "user_agent_tracking": self.ACTIVITY_LOG_USER_AGENT_TRACKING,
            "partition_interval": self.ACTIVITY_LOG_PARTITION_INTERVAL,
            "cleanup_enabled": self.ACTIVITY_LOG_CLEANUP_ENABLED,
            "cleanup_batch_size": self.ACTIVITY_LOG_CLEANUP_BATCH_SIZE
        }

    @property
    def verification_log_config(self) -> Dict[str, Any]:
        return {
            "retention_days": self.VERIFICATION_LOG_RETENTION_DAYS,
            "partition_interval": self.VERIFICATION_LOG_PARTITION_INTERVAL,
            "cleanup_enabled": self.VERIFICATION_LOG_CLEANUP_ENABLED,
            "cleanup_batch_size": self.VERIFICATION_LOG_CLEANUP_BATCH_SIZE
        }

settings = Settings() 