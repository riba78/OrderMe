"""
OrderMe Backend Application Entry Point - WORKING STATE REFERENCE

This is the main entry point for the OrderMe backend application.
This implementation is confirmed working with:
- User registration (MySQL storage)
- Admin authentication
- Regular user authentication
- Database management
- API routing

Key Working Features:
1. Admin User:
   - Email: admin@orderme.com
   - Password: admin123
   - Role: ADMIN
   - Auto-creation if not exists

2. Database Configuration:
   - MySQL integration
   - Automatic table creation
   - User management tables
   - Role-based access control

3. Security:
   - CORS configuration
   - JWT token validation
   - Password hashing
   - Role verification

4. API Routes:
   - /api/auth/* - Authentication routes
   - /api/admin/* - Admin routes
   - /api/user/* - User routes
   - Proper middleware
   - Error handling

DO NOT MODIFY this working implementation without thorough testing.

Environment Variables Required:
- DATABASE_URL: MySQL connection string
- ADMIN_EMAIL: Default admin user email
- ADMIN_PASSWORD: Default admin user password
- SECRET_KEY: Application secret key for JWT
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
from extensions import init_extensions, db
from models.user import User, UserRole
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
import logging
from werkzeug.exceptions import HTTPException
from config import settings

load_dotenv()

# Database URL configuration
db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")

def create_admin_user():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@orderme.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')  # Change in production!
    
    print(f"Checking for admin user with email: {admin_email}")
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        print("Admin user not found, creating...")
        admin = User(
            uuid=str(uuid.uuid4()),
            email=admin_email,
            role=UserRole.ADMIN.value,
            is_verified=True,
            is_active=True,
            created_as_role=UserRole.ADMIN.value
        )
        admin.set_password(admin_password)
        print(f"Generated password hash: {admin.password_hash}")
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created with email: {admin_email}")
    else:
        print("Admin user already exists")
        print(f"Existing admin password hash: {admin.password_hash}")

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = not settings.is_production
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    
    # For development, enable more detailed errors
    if not settings.is_production:
        app.config['PROPAGATE_EXCEPTIONS'] = True
        app.config['TRAP_HTTP_EXCEPTIONS'] = True
    
    # Enable activity logging
    settings.ACTIVITY_LOG_ENABLED = True
    
    # Initialize extensions
    init_extensions(app)
    
    # Setup logging
    if not settings.is_production:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Enable CORS
    CORS(app)

    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin == 'http://localhost:8080':
            # Always set CORS headers, even for errors
            response.headers.update({
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '3600',
                'Access-Control-Expose-Headers': 'Content-Type, Authorization'
            })
        return response

    # Global error handler to ensure CORS headers are set
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        
        if isinstance(e, HTTPException):
            return jsonify({"message": e.description}), e.code
        
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

    # Remove individual preflight routes as they're now handled globally
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_preflight(path):
        response = jsonify({'status': 'ok'})
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

    # Error handlers with proper CORS support
    @app.errorhandler(400)
    def bad_request_error(error):
        response = jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else str(error),
            'status_code': 400
        })
        response.status_code = 400
        return response

    @app.errorhandler(401)
    def unauthorized_error(error):
        response = jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource',
            'status_code': 401
        })
        response.status_code = 401
        return response

    @app.errorhandler(403)
    def forbidden_error(error):
        response = jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status_code': 403
        })
        response.status_code = 403
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        response = jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        })
        response.status_code = 404
        return response

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {str(error)}')
        response = jsonify({
            'error': 'Internal Server Error',
            'message': str(error) if app.debug else 'An unexpected error has occurred',
            'status_code': 500
        })
        response.status_code = 500
        return response

    # Register blueprints with /api prefix as per working state
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "ok", "message": "API is running"}), 200

    # Request logger
    @app.before_request
    def log_request_info():
        app.logger.debug('Request: %s %s', request.method, request.path)

    with app.app_context():
        # Create database tables
        db.create_all()
        # Create admin user
        create_admin_user()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 