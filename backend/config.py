"""
Application Configuration Module

This module manages all configuration settings for the application:

Environment Variables:
- DATABASE_URL: MySQL database connection string
- SECRET_KEY: Application secret key for JWT signing
- GOOGLE_CLIENT_ID: Google OAuth client ID
- FACEBOOK_APP_ID: Facebook application ID
- FACEBOOK_APP_SECRET: Facebook application secret
- ADMIN_EMAIL: Default admin user email
- ADMIN_PASSWORD: Default admin user password
- VERIFICATION_METHODS: Comma-separated list of enabled verification methods
- RATE_LIMIT_ATTEMPTS: Number of allowed attempts before rate limiting
- RATE_LIMIT_WINDOW: Time window for rate limiting in seconds
- ACTIVITY_LOG_ENABLED: Whether to enable activity logging

Features:
- Environment variable loading and validation
- Default value handling
- Configuration class for organized settings
- Development/production environment detection
- Secure credential management
- Rate limiting configuration
- Activity logging settings
- Verification method configuration

The module centralizes all configuration management and provides
a single source of truth for application settings.
"""

from pydantic import BaseSettings
from typing import Optional, List
from enum import Enum

class VerificationMethod(str, Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    GOOGLE = "GOOGLE"
    FACEBOOK = "FACEBOOK"

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: Optional[str] = None
    DB_SSL_CA: Optional[str] = None
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Facebook OAuth
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None

    # Verification settings
    VERIFICATION_METHODS: List[VerificationMethod] = [VerificationMethod.EMAIL]
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TEMPLATE: str = "email_verification.html"
    PHONE_VERIFICATION_TEMPLATE: str = "phone_verification.txt"

    # Rate limiting settings
    RATE_LIMIT_ATTEMPTS: int = 5
    RATE_LIMIT_WINDOW: int = 300  # 5 minutes in seconds
    RATE_LIMIT_BLOCK_DURATION: int = 900  # 15 minutes in seconds

    # Activity logging settings
    ACTIVITY_LOG_ENABLED: bool = True
    ACTIVITY_LOG_RETENTION_DAYS: int = 90
    ACTIVITY_LOG_IP_TRACKING: bool = True
    ACTIVITY_LOG_USER_AGENT_TRACKING: bool = True

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_production(self):
        return self.ENVIRONMENT.lower() == "production"

    @property
    def database_config(self):
        config = {"url": self.DATABASE_URL}
        if self.is_production and self.DB_SSL_CA:
            config["ssl_ca"] = self.DB_SSL_CA
        return config

    @property
    def verification_config(self):
        return {
            "methods": self.VERIFICATION_METHODS,
            "token_expire_minutes": self.VERIFICATION_TOKEN_EXPIRE_MINUTES,
            "email_template": self.EMAIL_VERIFICATION_TEMPLATE,
            "phone_template": self.PHONE_VERIFICATION_TEMPLATE
        }

    @property
    def rate_limit_config(self):
        return {
            "attempts": self.RATE_LIMIT_ATTEMPTS,
            "window": self.RATE_LIMIT_WINDOW,
            "block_duration": self.RATE_LIMIT_BLOCK_DURATION
        }

    @property
    def activity_log_config(self):
        return {
            "enabled": self.ACTIVITY_LOG_ENABLED,
            "retention_days": self.ACTIVITY_LOG_RETENTION_DAYS,
            "ip_tracking": self.ACTIVITY_LOG_IP_TRACKING,
            "user_agent_tracking": self.ACTIVITY_LOG_USER_AGENT_TRACKING
        }

settings = Settings() 