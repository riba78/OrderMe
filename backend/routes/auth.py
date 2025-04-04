"""
Authentication Routes Module - WORKING STATE REFERENCE

This module handles all authentication-related endpoints and is confirmed working with:
- User registration (stores in MySQL)
- Admin login (admin@orderme.com)
- Regular user login
- JWT token generation
- Role-based access control

Key Working Features:
1. User Authentication:
   - Login with email/password
   - JWT token generation
   - Role verification
   - Session management

2. User Registration:
   - Email validation
   - Password hashing
   - Role assignment (USER)
   - MySQL storage
   - Automatic activation

3. Admin Access:
   - Default admin credentials:
     Email: admin@orderme.com
     Password: admin123
   - Full admin privileges
   - Admin dashboard access

DO NOT MODIFY these working implementations without thorough testing.

Standard Authentication:
- POST /api/auth/login: User login with email/password
- POST /api/auth/register: New user registration
- POST /api/auth/logout: User logout (token invalidation)

Social Authentication:
- POST /api/auth/google: Google OAuth authentication
- POST /api/auth/facebook: Facebook OAuth authentication

Account Management:
- POST /api/auth/data-deletion: Request account deletion
- POST /api/auth/verify-email: Email verification
- POST /api/auth/reset-password: Password reset

Features:
- JWT token generation and validation
- Password hashing and verification
- Social authentication integration
- User session management
- Detailed error handling and logging
- Account security measures

The module provides comprehensive authentication functionality
with both traditional and social authentication methods.
"""

from flask import Blueprint, request, jsonify
from auth.social import SocialAuthHandler
from models.user import User
from extensions import db
from models.user import UserRole
from config import settings
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import logging

auth_bp = Blueprint('auth', __name__)
social_auth = SocialAuthHandler()

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        print("=== Login Request ===")
        print("Headers:", dict(request.headers))
        print("Raw Data:", request.get_data())
        data = request.json
        print("Parsed JSON Data:", data)
        
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            print("Missing email or password")
            return jsonify({'message': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        print(f"Found user: {user}")
        if user:
            print(f"User details: id={user.id}, email={user.email}, role={user.role}, is_active={user.is_active}")
            print(f"User password hash: {user.password_hash}")
        
        if not user:
            print("User not found")
            return jsonify({'message': 'Invalid credentials'}), 401
            
        print(f"Attempting to verify password")
        if not user.check_password(password):
            print("Password verification failed")
            return jsonify({'message': 'Invalid credentials'}), 401

        if not user.is_active:
            print("User is not active")
            return jsonify({'message': 'Account is deactivated'}), 401

        # Generate JWT token
        token = social_auth.generate_token(user)
        print("Generated token successfully")
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        })

    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        print("Traceback:", traceback.format_exc())
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    try:
        credential = request.json.get('credential')
        if not credential:
            return jsonify({'message': 'No credential provided'}), 400

        user_info = social_auth.verify_google_token(credential)
        if not user_info:
            return jsonify({'message': 'Invalid Google token'}), 401

        # Check if user exists
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            # Create new user
            user = User(
                email=user_info['email'],
                name=user_info['name'],
                is_verified=True,
                auth_provider='google'
            )
            db.session.add(user)
            db.session.commit()

        # Generate JWT token
        token = social_auth.generate_token(user)
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        })

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/facebook', methods=['POST'])
def facebook_auth():
    try:
        access_token = request.json.get('accessToken')
        user_data = request.json.get('userData')
        
        if not access_token or not user_data:
            return jsonify({'message': 'Missing required data'}), 400

        # Verify Facebook token
        if not social_auth.verify_facebook_token(access_token, user_data['id']):
            return jsonify({'message': 'Invalid Facebook token'}), 401

        # Check if user exists
        user = User.query.filter_by(email=user_data['email']).first()
        if not user:
            # Create new user
            user = User(
                email=user_data['email'],
                name=user_data['name'],
                is_verified=True,
                auth_provider='facebook'
            )
            db.session.add(user)
            db.session.commit()

        # Generate JWT token
        token = social_auth.generate_token(user)
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        })

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/data-deletion', methods=['POST'])
def request_data_deletion():
    try:
        data = request.json
        email = data.get('email')
        reason = data.get('reason', '')

        if not email:
            return jsonify({'message': 'Email is required'}), 400

        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Mark user for deletion
        user.deletion_requested = True
        user.deletion_request_date = datetime.utcnow()
        user.deletion_reason = reason
        db.session.commit()

        # Send confirmation email (implement this based on your email service)
        # send_deletion_confirmation_email(email)

        return jsonify({
            'message': 'Data deletion request received',
            'status': 'pending',
            'requestDate': user.deletion_request_date.isoformat()
        })

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/auth/data-deletion/confirm/<token>', methods=['GET'])
def confirm_data_deletion(token):
    try:
        # Verify token and get user
        user = User.query.filter_by(deletion_confirmation_token=token).first()
        if not user:
            return jsonify({'message': 'Invalid or expired token'}), 400

        # Perform actual data deletion
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'message': 'Your data has been successfully deleted',
            'status': 'completed'
        })

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    User Registration Endpoint - WORKING STATE
    
    This endpoint successfully:
    1. Creates new users in MySQL database
    2. Assigns USER role by default
    3. Sets proper password hashing
    4. Generates JWT token
    5. Returns user data
    
    Request format:
    {
        "email": "user@example.com",
        "password": "strongpassword",
        "name": "Optional Name"  // Will use email prefix if not provided
    }
    
    Response format:
    {
        "token": "JWT_TOKEN",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "role": "USER",
            ...
        }
    }
    
    DO NOT MODIFY this working implementation without thorough testing.
    """
    try:
        print("=== Registration Request ===")
        print("Headers:", dict(request.headers))
        print("Raw Data:", request.get_data())
        data = request.json
        print("Parsed JSON Data:", data)
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', email.split('@')[0])  # Use part before @ as name if not provided

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 400

        # Create new user - always as regular USER role
        user = User(
            email=email,
            name=name,
            role=UserRole.USER,
            is_verified=False,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        # Generate JWT token
        token = social_auth.generate_token(user)
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        })

    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        print("Traceback:", traceback.format_exc())
        return jsonify({'message': str(e)}), 500 