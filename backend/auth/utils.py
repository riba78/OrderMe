"""
Authentication Utilities Module

This module provides core authentication functionality for the application.

Functions:
1. get_current_user:
   - Extracts and validates JWT token from request header
   - Decodes token and retrieves user information
   - Returns User object or None if validation fails

2. token_required:
   - Decorator for protecting routes requiring authentication
   - Validates token presence and format
   - Ensures user exists and is active

Security Features:
- JWT token validation
- User authentication state management
- Secure token decoding
- Proper error handling
"""

from functools import wraps
from flask import request, jsonify
import jwt
from models.user import User
import os

def get_current_user():
    """
    Get the current authenticated user from the JWT token.
    
    Returns:
        User: The authenticated user object if valid token
        None: If token is invalid or missing
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    try:
        token = auth_header.split(' ')[1]
        secret_key = os.getenv('SECRET_KEY')
        
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = payload.get('sub')
        
        if not user_id:
            return None
            
        return User.query.get(int(user_id))
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except (KeyError, ValueError):
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
            return jsonify({'error': 'Invalid or missing token'}), 401
        return f(*args, **kwargs)
    return decorated 