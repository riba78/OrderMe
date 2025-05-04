# backend/app/__init__.py

__version__ = "1.0.0"
 
 # Application configuration from main.py
APP_NAME = "User and Auth API"
APP_DESCRIPTION = "API for user management and authentication services"

# Export the FastAPI app instance
from .main import app
from .database import get_async_session

__all__ = [
 "app",
 "APP_NAME",
 "APP_DESCRIPTION",
 "__version__",
 "get_async_session"
]