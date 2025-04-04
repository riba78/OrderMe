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

Security Features:
- JWT token validation
- User authentication state management
- Secure token decoding
- Role validation
- Proper error handling
"""

from functools import wraps
from flask import request, jsonify
import jwt
from models.user import User
from config import settings

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
            return jsonify({'error': 'Invalid or missing token'}), 401
        return f(*args, **kwargs)
    return decorated 