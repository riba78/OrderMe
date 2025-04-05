"""
OrderMe Backend Application

This is the main entry point for the OrderMe backend application with:
- Enhanced database configuration with connection pooling
- Comprehensive security measures
- Activity and verification logging
- Rate limiting and CORS
- Error handling and monitoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from extensions import init_extensions, db
from models.user import User, UserRole, UserProfile
from models.activity_log import ActivityLog
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from config import settings
import uuid

# Load environment variables
load_dotenv()

def setup_logging(app):
    """Configure application logging."""
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    file_handler = RotatingFileHandler(
        'logs/orderme.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('OrderMe startup')

def create_admin_user():
    """Create or update admin user with enhanced profile."""
    try:
        admin = User.query.filter_by(email=settings.ADMIN_EMAIL).first()
        
        if not admin:
            admin = User(
                uuid=str(uuid.uuid4()),
                email=settings.ADMIN_EMAIL,
                role=UserRole.ADMIN,
                is_verified=True,
                is_active=True,
                created_as_role=UserRole.SYSTEM
            )
            admin.set_password(settings.ADMIN_PASSWORD)
            
            # Create admin profile
            profile = UserProfile(
                first_name=settings.ADMIN_FIRST_NAME,
                last_name=settings.ADMIN_LAST_NAME,
                timezone=settings.DEFAULT_TIMEZONE,
                language=settings.DEFAULT_LANGUAGE
            )
            admin.profile = profile
            
            db.session.add(admin)
            db.session.commit()
            
            # Log admin creation
            activity = ActivityLog(
                user_id=admin.id,
                action_type='admin_created',
                metadata={'email': admin.email}
            )
            db.session.add(activity)
            db.session.commit()
            
            logging.info(f"Admin user created: {admin.email}")
        else:
            # Update admin if needed
            if not admin.profile:
                profile = UserProfile(
                    first_name=settings.ADMIN_FIRST_NAME,
                    last_name=settings.ADMIN_LAST_NAME,
                    timezone=settings.DEFAULT_TIMEZONE,
                    language=settings.DEFAULT_LANGUAGE
                )
                admin.profile = profile
                db.session.commit()
                logging.info(f"Admin profile updated: {admin.email}")
            
            logging.info(f"Admin user exists: {admin.email}")
    
    except Exception as e:
        logging.error(f"Error creating/updating admin user: {str(e)}")
        db.session.rollback()
        raise

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    setup_logging(app)
    
    # Configure CORS with enhanced security
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:8080"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Accept"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })

    # CORS headers middleware
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin == 'http://localhost:8080':
            response.headers.update({
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '3600',
                'Access-Control-Expose-Headers': 'Content-Type, Authorization'
            })
        return response

    # Error handlers with enhanced logging
    @app.errorhandler(400)
    def bad_request_error(error):
        logging.warning(f"Bad request: {str(error)}")
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description),
            'code': 'BAD_REQUEST'
        }), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        logging.warning(f"Unauthorized access attempt: {str(error)}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required',
            'code': 'UNAUTHORIZED'
        }), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        logging.warning(f"Forbidden access attempt: {str(error)}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions',
            'code': 'FORBIDDEN'
        }), 403

    @app.errorhandler(404)
    def not_found_error(error):
        logging.info(f"Resource not found: {request.path}")
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found',
            'code': 'NOT_FOUND'
        }), 404

    @app.errorhandler(429)
    def ratelimit_error(error):
        logging.warning(f"Rate limit exceeded: {request.remote_addr}")
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded',
            'code': 'RATE_LIMIT_EXCEEDED'
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'code': 'INTERNAL_ERROR'
        }), 500

    # Configure SQLAlchemy with enhanced settings
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = settings.database_config
    app.config['SECRET_KEY'] = settings.JWT_SECRET_KEY

    # Initialize extensions
    init_extensions(app)

    # Register blueprints with API versioning
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(user_bp, url_prefix='/api/v1/user')

    # Initialize database and admin user
    with app.app_context():
        try:
            # Create database tables
            db.create_all()
            
            # Create admin user
            create_admin_user()
            
            logging.info("Application initialization completed successfully")
            
        except Exception as e:
            logging.error(f"Application initialization failed: {str(e)}")
            raise

    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Run with enhanced debugging in development
    debug = not settings.is_production
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=debug,
        use_reloader=debug
    ) 