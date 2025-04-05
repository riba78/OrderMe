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

import os
from dotenv import load_dotenv
from typing import Optional, List
from enum import Enum

# Load environment variables from .env file
load_dotenv()

class VerificationMethod(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    WHATSAPP = "whatsapp"

class Settings:
    def __init__(self):
        # Database settings
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.DB_SSL_CA = os.getenv('DB_SSL_CA')
        
        # JWT settings
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
        self.ALGORITHM = os.getenv('ALGORITHM', 'HS256')
        self.ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv('ACCESS_TOKEN_EXPIRE_DAYS', '30'))

        # Google OAuth
        self.GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        self.GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

        # Facebook OAuth
        self.FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
        self.FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')

        # Verification settings
        verification_methods = os.getenv('VERIFICATION_METHODS', 'EMAIL')
        self.VERIFICATION_METHODS = [VerificationMethod(method.strip()) for method in verification_methods.split(',')]
        self.VERIFICATION_TOKEN_EXPIRE_MINUTES = int(os.getenv('VERIFICATION_TOKEN_EXPIRE_MINUTES', '30'))
        self.EMAIL_VERIFICATION_TEMPLATE = os.getenv('EMAIL_VERIFICATION_TEMPLATE', 'email_verification.html')
        self.PHONE_VERIFICATION_TEMPLATE = os.getenv('PHONE_VERIFICATION_TEMPLATE', 'phone_verification.txt')

        # Rate limiting settings
        self.RATE_LIMIT_ATTEMPTS = int(os.getenv('RATE_LIMIT_ATTEMPTS', '5'))
        self.RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '300'))
        self.RATE_LIMIT_BLOCK_DURATION = int(os.getenv('RATE_LIMIT_BLOCK_DURATION', '900'))

        # Activity logging settings
        self.ACTIVITY_LOG_ENABLED = os.getenv('ACTIVITY_LOG_ENABLED', 'true').lower() == 'true'
        self.ACTIVITY_LOG_RETENTION_DAYS = int(os.getenv('ACTIVITY_LOG_RETENTION_DAYS', '90'))
        self.ACTIVITY_LOG_IP_TRACKING = os.getenv('ACTIVITY_LOG_IP_TRACKING', 'true').lower() == 'true'
        self.ACTIVITY_LOG_USER_AGENT_TRACKING = os.getenv('ACTIVITY_LOG_USER_AGENT_TRACKING', 'true').lower() == 'true'

        # Environment
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

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