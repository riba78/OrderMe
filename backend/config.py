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

Features:
- Environment variable loading and validation
- Default value handling
- Configuration class for organized settings
- Development/production environment detection
- Secure credential management

The module centralizes all configuration management and provides
a single source of truth for application settings.
"""

from pydantic import BaseSettings
from typing import Optional

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

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

    @property
    def is_production(self):
        return self.ENVIRONMENT.lower() == "production"

    @property
    def database_config(self):
        config = {"url": self.DATABASE_URL}
        if self.is_production and self.DB_SSL_CA:
            config["ssl_ca"] = self.DB_SSL_CA
        return config

settings = Settings() 