"""
Authentication Utilities Module

This module provides core authentication functionality for the application.

Functions:
1. get_current_user:
   - Extracts and validates JWT token from request header
   - Decodes token and retrieves user information
   - Returns User object or None if validation fails
   - Validates user role matches token role

2. token_required:
   - Decorator for protecting routes requiring authentication
   - Validates token presence and format
   - Ensures user exists and is active
   - Logs authentication attempts

3. rate_limit:
   - Decorator for implementing rate limiting
   - Tracks attempts per IP address
   - Implements blocking after too many attempts
   - Configurable window and block duration

4. log_activity:
   - Logs user activities and system events
   - Tracks IP addresses and user agents
   - Stores metadata about the activity
   - Respects activity logging settings

Security Features:
- JWT token validation
- User authentication state management
- Secure token decoding
- Role validation
- Rate limiting
- Activity logging
- IP tracking
- User agent tracking
- Proper error handling
"""

from functools import wraps
from flask import request, jsonify, g
import jwt
from models.user import User
from models.activity_log import ActivityLog
from config import settings
import time
import logging

# Rate limiting implementation
rate_limit_data = {}

def rate_limit(f):
    """
    Decorator to implement rate limiting on routes.
    
    Args:
        f: The route function to protect
    
    Returns:
        function: The decorated function that implements rate limiting
    """
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
    """
    Log user activity if enabled in settings.
    
    Args:
        user_id: ID of the user performing the activity
        activity_type: Type of activity (e.g., 'login', 'register')
        entity_type: Type of entity affected (e.g., 'user', 'customer')
        entity_id: ID of the entity affected
        metadata: Additional information about the activity
    """
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

def get_current_user():
    """
    Get the current authenticated user from the JWT token.
    Also validates that the user's role matches the role in the token.
    
    Returns:
        User: The authenticated user object if valid token and role
        None: If token is invalid, missing, or role mismatch
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        print("Missing or invalid Authorization header")
        return None
    
    try:
        token = auth_header.split(' ')[1]
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get('sub')
        token_role = payload.get('role')
        
        if not user_id or not token_role:
            print("Missing user_id or role in token")
            return None
            
        user = User.query.get(int(user_id))
        if not user:
            print(f"User {user_id} not found")
            return None
            
        # Validate that the user's current role matches the role in the token
        if user.role.value != token_role:
            print(f"Role mismatch - Token: {token_role}, User: {user.role.value}")
            return None
            
        # Log successful authentication
        log_activity(
            user_id=user.id,
            activity_type='token_validation',
            metadata={'status': 'success'}
        )
            
        return user
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Token parsing error: {str(e)}")
        return None

def token_required(f):
    """
    Decorator to protect routes requiring authentication.
    
    Args:
        f: The route function to protect
    
    Returns:
        function: The decorated function that checks for valid authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            # Log failed authentication attempt
            log_activity(
                user_id=None,
                activity_type='token_validation',
                metadata={'status': 'failed', 'reason': 'invalid_token'}
            )
            return jsonify({'error': 'Invalid or missing token'}), 401
        return f(*args, **kwargs)
    return decorated 