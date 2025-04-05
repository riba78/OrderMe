"""
Authentication Module

This module provides authentication utilities and decorators with:
- JWT token management
- Role-based access control
- Activity logging
- Rate limiting
- Security measures
"""

from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from datetime import datetime, timedelta
from models.user import User, UserRole
from models.activity_log import ActivityLog
from config import settings
import logging

def get_current_user():
    """Get the current user from the request context with enhanced security."""
    if not hasattr(g, 'current_user'):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            # Decode token with enhanced validation
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM],
                options={
                    'verify_exp': True,
                    'verify_iat': True,
                    'require': ['exp', 'iat', 'sub', 'type']
                }
            )
            
            # Validate token type and expiration
            if payload.get('type') != 'access':
                return None
                
            user_id = payload.get('sub')
            if not user_id:
                return None

            # Get user and verify status
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return None

            # Store in context
            g.current_user = user
            
            # Update last activity
            user.last_activity_at = datetime.utcnow()
            
            # Log activity if enabled
            if settings.ACTIVITY_LOG_ENABLED:
                try:
                    activity = ActivityLog(
                        user_id=user.id,
                        action_type='auth_check',
                        ip_address=request.remote_addr,
                        user_agent=request.user_agent.string
                    )
                    from extensions import db
                    db.session.add(activity)
                    db.session.commit()
                except Exception as e:
                    logging.error(f"Failed to log auth activity: {str(e)}")
            
            return user
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            logging.error(f"Auth error: {str(e)}")
            return None
    
    return g.current_user

def login_required(f):
    """Decorator to require login with enhanced security."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
        if not current_user.is_active:
            return jsonify({'error': 'Account is deactivated', 'code': 'ACCOUNT_INACTIVE'}), 403
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to require specific roles with enhanced security."""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not g.current_user.role or g.current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions', 'code': 'INSUFFICIENT_PERMISSIONS'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role."""
    return role_required(UserRole.ADMIN)(f)

def create_token(user_id: int, token_type: str = 'access') -> str:
    """Create a new JWT token with enhanced security."""
    now = datetime.utcnow()
    
    if token_type == 'access':
        expire = now + timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
    elif token_type == 'refresh':
        expire = now + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES)
    else:
        raise ValueError('Invalid token type')
    
    to_encode = {
        'exp': expire,
        'iat': now,
        'sub': str(user_id),
        'type': token_type
    }
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def create_temp_token(user_id: int, purpose: str, expire_minutes: int = 30) -> str:
    """Create a temporary token for verification purposes."""
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    
    to_encode = {
        'exp': expire,
        'iat': now,
        'sub': str(user_id),
        'type': 'temp',
        'purpose': purpose
    }
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def verify_temp_token(token: str, purpose: str = None) -> User:
    """Verify a temporary token and return the associated user."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                'verify_exp': True,
                'verify_iat': True,
                'require': ['exp', 'iat', 'sub', 'type', 'purpose']
            }
        )
        
        if payload.get('type') != 'temp':
            return None
            
        if purpose and payload.get('purpose') != purpose:
            return None
            
        user_id = payload.get('sub')
        if not user_id:
            return None
            
        return User.query.get(user_id)
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception as e:
        logging.error(f"Temp token verification error: {str(e)}")
        return None 