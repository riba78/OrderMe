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
   - Proper middleware
   - Error handling

DO NOT MODIFY this working implementation without thorough testing.

Environment Variables Required:
- DATABASE_URL: MySQL connection string
- ADMIN_EMAIL: Default admin user email
- ADMIN_PASSWORD: Default admin user password
- SECRET_KEY: Application secret key for JWT
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from extensions import init_extensions, db
from models.user import User, UserRole

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
            email=admin_email,
            name='Admin',
            role=UserRole.ADMIN,
            is_verified=True,
            is_active=True
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
    
    # Configure CORS with more permissive settings for development
    CORS(app, 
         resources={r"/api/*": {
             "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }})

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # Initialize extensions
    init_extensions(app)

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    with app.app_context():
        # Create database tables
        db.create_all()
        # Create admin user
        create_admin_user()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 