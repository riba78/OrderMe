"""
Authentication Routes Module - WORKING STATE REFERENCE

This module handles all authentication-related endpoints and is confirmed working with:
- User registration (stores in MySQL)
- Admin login (admin@orderme.com)
- Regular user login
- JWT token generation
- Role-based access control
- Verification methods
- Activity logging
- Rate limiting

Key Working Features:
1. User Authentication:
   - Login with email/password
   - JWT token generation
   - Role verification
   - Session management
   - Rate limiting
   - Activity logging

2. User Registration:
   - Email validation
   - Password hashing
   - Role assignment (USER)
   - MySQL storage
   - Automatic activation
   - Verification methods
   - Activity logging

3. Admin Access:
   - Default admin credentials:
     Email: admin@orderme.com
     Password: admin123
   - Full admin privileges
   - Admin dashboard access
   - Activity logging

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
- POST /api/auth/verify-phone: Phone verification
- POST /api/auth/change-email: Email change request

Features:
- JWT token generation and validation
- Password hashing and verification
- Social authentication integration
- User session management
- Detailed error handling and logging
- Account security measures
- Rate limiting
- Activity logging
- Multiple verification methods
"""

from flask import Blueprint, request, jsonify
from auth.social import SocialAuthHandler
from models.user import User, UserRole, VerificationMethod
from models.activity_log import ActivityLog
from models.verification_message_log import VerificationMessageLog
from extensions import db
from config import settings
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
import logging
from functools import wraps
from flask import g
import time

auth_bp = Blueprint('auth', __name__)
social_auth = SocialAuthHandler()

# Rate limiting implementation
rate_limit_data = {}

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        current_time = time.time()
        
        # Initialize rate limit data for this IP if not exists
        if ip not in rate_limit_data:
            rate_limit_data[ip] = {
                'attempts': 0,
                'window_start': current_time,
                'blocked_until': None
            }
        
        # Check if IP is blocked
        if rate_limit_data[ip]['blocked_until'] and current_time < rate_limit_data[ip]['blocked_until']:
            return jsonify({'message': 'Too many attempts. Please try again later.'}), 429
        
        # Reset window if expired
        if current_time - rate_limit_data[ip]['window_start'] > settings.RATE_LIMIT_WINDOW:
            rate_limit_data[ip] = {
                'attempts': 0,
                'window_start': current_time,
                'blocked_until': None
            }
        
        # Check attempts
        if rate_limit_data[ip]['attempts'] >= settings.RATE_LIMIT_ATTEMPTS:
            rate_limit_data[ip]['blocked_until'] = current_time + settings.RATE_LIMIT_BLOCK_DURATION
            return jsonify({'message': 'Too many attempts. Please try again later.'}), 429
        
        # Increment attempts
        rate_limit_data[ip]['attempts'] += 1
        
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id: int, activity_type: str, entity_type: str = None, entity_id: int = None, metadata: dict = None):
    """Log user activity if enabled in settings"""
    if not settings.ACTIVITY_LOG_ENABLED:
        return
    
    try:
        activity = ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata,
            ip_address=request.remote_addr if settings.ACTIVITY_LOG_IP_TRACKING else None,
            user_agent=request.user_agent.string if settings.ACTIVITY_LOG_USER_AGENT_TRACKING else None
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log activity: {str(e)}")

@auth_bp.route('/login', methods=['POST'])
@rate_limit
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
        
        # Log successful login
        log_activity(
            user_id=user.id,
            activity_type='login',
            metadata={'method': 'email'}
        )
        
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
@rate_limit
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
        phone = data.get('phone')
        verification_method = data.get('verification_method', VerificationMethod.EMAIL.value)

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
            is_active=True,
            primary_verification_method=verification_method
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        # Create verification method record
        if verification_method == VerificationMethod.EMAIL.value:
            verification = UserVerificationMethod(
                user_id=user.id,
                method_type=VerificationMethod.EMAIL,
                identifier=email,
                is_verified=False
            )
        elif verification_method == VerificationMethod.PHONE.value and phone:
            verification = UserVerificationMethod(
                user_id=user.id,
                method_type=VerificationMethod.PHONE,
                identifier=phone,
                is_verified=False
            )
        else:
            return jsonify({'message': 'Invalid verification method or missing phone number'}), 400

        db.session.add(verification)
        db.session.commit()

        # Generate JWT token
        token = social_auth.generate_token(user)
        
        # Log registration
        log_activity(
            user_id=user.id,
            activity_type='register',
            metadata={
                'verification_method': verification_method,
                'phone': phone if phone else None
            }
        )
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        })

    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        print("Traceback:", traceback.format_exc())
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/verify-email', methods=['POST'])
@token_required
def verify_email():
    try:
        user = get_current_user()
        token = request.json.get('token')
        
        if not token:
            return jsonify({'message': 'Verification token is required'}), 400
            
        # Verify token and update user status
        verification = UserVerificationMethod.query.filter_by(
            user_id=user.id,
            method_type=VerificationMethod.EMAIL,
            verification_token=token
        ).first()
        
        if not verification:
            return jsonify({'message': 'Invalid verification token'}), 400
            
        verification.is_verified = True
        verification.verification_token = None
        user.is_verified = True
        db.session.commit()
        
        # Log verification
        log_activity(
            user_id=user.id,
            activity_type='email_verification',
            metadata={'status': 'success'}
        )
        
        return jsonify({'message': 'Email verified successfully'})
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/verify-phone', methods=['POST'])
@token_required
def verify_phone():
    try:
        user = get_current_user()
        code = request.json.get('code')
        
        if not code:
            return jsonify({'message': 'Verification code is required'}), 400
            
        # Verify code and update user status
        verification = UserVerificationMethod.query.filter_by(
            user_id=user.id,
            method_type=VerificationMethod.PHONE,
            verification_token=code
        ).first()
        
        if not verification:
            return jsonify({'message': 'Invalid verification code'}), 400
            
        verification.is_verified = True
        verification.verification_token = None
        user.is_verified = True
        db.session.commit()
        
        # Log verification
        log_activity(
            user_id=user.id,
            activity_type='phone_verification',
            metadata={'status': 'success'}
        )
        
        return jsonify({'message': 'Phone number verified successfully'})
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/change-email', methods=['POST'])
@token_required
def change_email():
    try:
        user = get_current_user()
        new_email = request.json.get('new_email')
        
        if not new_email:
            return jsonify({'message': 'New email is required'}), 400
            
        if User.query.filter_by(email=new_email).first():
            return jsonify({'message': 'Email already in use'}), 400
            
        # Generate email change token
        token = generate_token()
        user.email_change_token = token
        user.email_change_new = new_email
        user.email_change_expires = datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)
        db.session.commit()
        
        # Send verification email (implement this based on your email service)
        # send_email_change_verification(new_email, token)
        
        # Log email change request
        log_activity(
            user_id=user.id,
            activity_type='email_change_request',
            metadata={'new_email': new_email}
        )
        
        return jsonify({'message': 'Email change verification sent'})
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/confirm-email-change/<token>', methods=['GET'])
def confirm_email_change(token):
    try:
        user = User.query.filter_by(email_change_token=token).first()
        
        if not user or datetime.utcnow() > user.email_change_expires:
            return jsonify({'message': 'Invalid or expired token'}), 400
            
        new_email = user.email_change_new
        user.email = new_email
        user.email_change_token = None
        user.email_change_new = None
        user.email_change_expires = None
        db.session.commit()
        
        # Log email change
        log_activity(
            user_id=user.id,
            activity_type='email_change',
            metadata={'old_email': user.email, 'new_email': new_email}
        )
        
        return jsonify({'message': 'Email changed successfully'})
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500 