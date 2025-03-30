"""
Flask Extensions Module

This module initializes and manages Flask extensions used throughout the application.
Currently manages:
- SQLAlchemy: Database ORM for MySQL interactions
- Other extensions can be added here as needed

The init_extensions function should be called during app initialization to properly
set up all extensions with the Flask application instance.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db) 