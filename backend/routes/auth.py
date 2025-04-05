"""
Authentication Routes Module

This module handles all authentication-related endpoints with:
- User registration with verification methods
- Multi-factor authentication
- Activity logging with partitioning
- Rate limiting and security
- Session management
- Role-based access control

Key Features:
1. User Authentication:
   - Login with email/password
   - JWT token generation
   - Role verification
   - Session management
   - Rate limiting
   - Activity logging

2. User Registration:
   - Email/Phone verification
   - Password hashing
   - Role assignment
   - Profile creation
   - Verification method selection
   - Activity logging

3. Verification Methods:
   - Email verification
   - Phone verification
   - Social authentication
   - Multi-factor support
   - Verification logging
"""

from flask import Blueprint, request, jsonify, current_app
from auth.social import SocialAuthHandler
from models import User, UserRole, VerificationMethod, UserProfile, UserVerificationMethod
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
import uuid
import jwt
import traceback

auth_bp = Blueprint('auth', __name__)
social_auth = SocialAuthHandler()

@auth_bp.route('/debug-login', methods=['POST'])
def debug_login():
    """Simple login endpoint for debugging"""
    try:
        data = request.json
        if not data:
            return jsonify({"message": "Missing request data"}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        # Find user by email with explicit query
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"message": "Invalid credentials"}), 401

        # Check password
        if not check_password_hash(user.password_hash, password):
            return jsonify({"message": "Invalid credentials"}), 401

        # Generate a simple token
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'sub': str(user.id),
            'email': user.email,
            'role': str(user.role)
        }
        
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        # Return the token without using to_dict
        return jsonify({
            'access_token': token,
            'refresh_token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': str(user.role)
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

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

def log_activity(user_id: int, action_type: str, entity_type: str = None, 
                entity_id: int = None, metadata: dict = None):
    """Log user activity with enhanced tracking"""
    if not settings.ACTIVITY_LOG_ENABLED:
        return
    
    try:
        activity = ActivityLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            meta_data=metadata,
            ip_address=request.remote_addr if settings.ACTIVITY_LOG_IP_TRACKING else None,
            user_agent=request.user_agent.string if settings.ACTIVITY_LOG_USER_AGENT_TRACKING else None
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log activity: {str(e)}")

def log_verification_message(user_id: int, method_type: str, message_type: str,
                           identifier: str, status: str, provider: str,
                           provider_message_id: str = None, error_message: str = None,
                           metadata: dict = None):
    """Log verification message attempts"""
    try:
        message_log = VerificationMessageLog(
            user_id=user_id,
            method_type=method_type,
            message_type=message_type,
            identifier=identifier,
            status=status,
            provider=provider,
            provider_message_id=provider_message_id,
            error_message=error_message,
            metadata=metadata
        )
        db.session.add(message_log)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log verification message: {str(e)}")

@auth_bp.route('/login', methods=['POST'])
@rate_limit
def login():
    try:
        data = request.json
        if not data:
            return jsonify({'message': 'Missing request data'}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        
        if not user:
            logging.warning(f"Login attempt for non-existent user: {email}")
            return jsonify({'message': 'Invalid credentials'}), 401
            
        if not hasattr(user, 'check_password'):
            logging.error(f"User {email} missing check_password method")
            if hasattr(user, 'verify_password'):
                password_valid = user.verify_password(password)
            else:
                logging.error(f"User {email} has no password verification method")
                return jsonify({'message': 'Authentication error'}), 500
        else:
            password_valid = user.check_password(password)
            
        if not password_valid:
            # Log failed login attempt
            log_activity(
                user_id=user.id,
                action_type='login_failed',
                metadata={'reason': 'invalid_password'}
            )
            return jsonify({'message': 'Invalid credentials'}), 401

        if not user.is_active:
            log_activity(
                user_id=user.id,
                action_type='login_failed',
                metadata={'reason': 'account_inactive'}
            )
            return jsonify({'message': 'Account is deactivated'}), 401

        # Check if verification is required
        if not user.is_verified and user.primary_verification_method:
            # Send verification code
            verification_sent = send_verification_code(
                user,
                user.primary_verification_method,
                'login_verification'
            )
            if verification_sent:
                return jsonify({
                    'message': 'Verification required',
                    'verification_method': str(user.primary_verification_method),
                    'temp_token': generate_temp_token(user)
                }), 202

        # Generate JWT token
        try:
            token = social_auth.generate_token(user)
        except Exception as token_error:
            logging.error(f"Token generation error: {str(token_error)}")
            return jsonify({'message': 'Error generating authentication token'}), 500
        
        # Update login stats
        try:
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
            db.session.commit()
        except Exception as db_error:
            logging.error(f"Error updating login stats: {str(db_error)}")
            db.session.rollback()
        
        # Log successful login
        try:
            log_activity(
                user_id=user.id,
                action_type='login',
                metadata={
                    'method': 'email',
                    'login_count': user.login_count
                }
            )
        except Exception as log_error:
            logging.error(f"Error logging login activity: {str(log_error)}")
        
        return jsonify({
            'access_token': token,
            'refresh_token': token,  # For simplicity, using same token
            'user': user.to_dict()
        })

    except Exception as e:
        logging.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/register', methods=['POST'])
@rate_limit
def register():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['email', 'password', 'verification_method']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400

        # Create user
        user = User(
            uuid=str(uuid.uuid4()),
            email=data['email'],
            role=UserRole.USER,
            is_active=True,
            is_verified=False,
            primary_verification_method=VerificationMethod.coerce(data['verification_method']),
            created_as_role=UserRole.SYSTEM
        )
        user.set_password(data['password'])

        # Create user profile
        profile = UserProfile(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number')
        )
        user.profile = profile

        # Add verification method
        verification_method = user.add_verification_method(
            method_type=data['verification_method'],
            identifier=data['email'] if data['verification_method'] == 'EMAIL' else data.get('phone_number')
        )

        db.session.add(user)
        db.session.commit()

        # Send verification code
        verification_sent = send_verification_code(
            user,
            data['verification_method'],
            'registration'
        )

        # Log registration
        log_activity(
            user_id=user.id,
            action_type='register',
            metadata={
                'verification_method': data['verification_method'],
                'verification_sent': verification_sent
            }
        )

        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict(),
            'verification_required': True,
            'verification_method': data['verification_method']
        }), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['verification_token', 'code']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400

        # Get user from verification token
        user = verify_temp_token(data['verification_token'])
        if not user:
            return jsonify({'message': 'Invalid verification token'}), 401

        # Verify code
        verification_method = user.get_verification_method(user.primary_verification_method)
        if not verification_method:
            return jsonify({'message': 'No verification method found'}), 400

        if not verification_method.verify_code(data['code']):
            # Log failed verification
            log_verification_message(
                user_id=user.id,
                method_type=str(user.primary_verification_method),
                message_type='verification',
                identifier=verification_method.identifier,
                status='failed',
                provider='system',
                error_message='Invalid code'
            )
            return jsonify({'message': 'Invalid verification code'}), 401

        # Mark as verified
        user.is_verified = True
        verification_method.mark_as_verified()
        db.session.commit()

        # Log successful verification
        log_activity(
            user_id=user.id,
            action_type='verify',
            metadata={
                'method': str(user.primary_verification_method),
                'identifier': verification_method.identifier
            }
        )

        # Generate final token
        token = social_auth.generate_token(user)

        return jsonify({
            'message': 'Verification successful',
            'token': token,
            'user': user.to_dict()
        })

    except Exception as e:
        logging.error(f"Verification error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data = request.json
        
        # Get user from verification token
        user = verify_temp_token(data.get('verification_token'))
        if not user:
            return jsonify({'message': 'Invalid verification token'}), 401

        # Check rate limiting for resend
        verification_method = user.get_verification_method(user.primary_verification_method)
        if not verification_method:
            return jsonify({'message': 'No verification method found'}), 400

        if verification_method.is_rate_limited():
            return jsonify({'message': 'Too many attempts. Please try again later.'}), 429

        # Send new verification code
        verification_sent = send_verification_code(
            user,
            user.primary_verification_method,
            'resend'
        )

        if not verification_sent:
            return jsonify({'message': 'Failed to send verification code'}), 500

        return jsonify({
            'message': 'Verification code resent',
            'verification_method': str(user.primary_verification_method)
        })

    except Exception as e:
        logging.error(f"Resend verification error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@rate_limit
def refresh_token():
    """Refresh access token using refresh token."""
    try:
        data = request.json
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'message': 'Refresh token is required'}), 400
            
        # Decode the refresh token
        try:
            payload = jwt.decode(
                refresh_token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get('sub')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Refresh token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid refresh token'}), 401
            
        # Get the user
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        if not user.is_active:
            return jsonify({'message': 'User account is inactive'}), 401
            
        # Generate new tokens
        new_token = social_auth.generate_token(user)
        
        return jsonify({
            'access_token': new_token,
            'refresh_token': refresh_token  # Reuse the same refresh token for simplicity
        })
    except Exception as e:
        logging.error(f"Token refresh error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/request-verification', methods=['POST'])
def request_verification():
    """Request a verification code for a user"""
    try:
        data = request.json
        if not data or not data.get('email') or not data.get('method'):
            return jsonify({"message": "Email and method are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Send verification code
        method = data['method']
        verification_sent = send_verification_code(user, method, 'verification')
        
        if not verification_sent:
            return jsonify({"message": "Failed to send verification"}), 500
        
        return jsonify({
            "message": "Verification code sent successfully",
            "method": method
        }), 200
    except Exception as e:
        logging.error(f"Verification request error: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500

def send_verification_code(user: User, method_type: str, purpose: str) -> bool:
    """Send verification code using specified method"""
    try:
        verification_method = user.get_verification_method(method_type)
        if not verification_method:
            return False

        code = verification_method.generate_code()
        
        if method_type == VerificationMethod.EMAIL:
            # Send email
            sent = send_verification_email(
                user.email,
                code,
                purpose
            )
        elif method_type == VerificationMethod.PHONE:
            # Send SMS
            sent = send_verification_sms(
                verification_method.identifier,
                code,
                purpose
            )
        else:
            return False

        if sent:
            # Log verification message
            log_verification_message(
                user_id=user.id,
                method_type=method_type,
                message_type=purpose,
                identifier=verification_method.identifier,
                status='sent',
                provider='system',
                metadata={'purpose': purpose}
            )
            return True
        
        return False

    except Exception as e:
        logging.error(f"Send verification code error: {str(e)}")
        return False 