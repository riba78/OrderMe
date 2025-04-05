"""
Authentication Decorators Module

This module provides decorators for authentication and authorization:
1. token_required: Verify JWT token and load current user
2. admin_required: Ensure user has admin role
3. rate_limit: Apply rate limiting to routes
"""

from functools import wraps
from datetime import datetime
import logging
from flask import request, jsonify, g
import jwt
from models import User, UserRole
from config import settings

def get_current_user():
    """Get the current authenticated user."""
    return getattr(g, 'current_user', None)

def token_required(f):
    """Decorator to verify JWT token and load current user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Decode token
            data = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Get user
            current_user = User.query.get(data['sub'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
            
            if not current_user.is_active:
                return jsonify({'message': 'User is inactive'}), 401
            
            # Store user in flask g object
            g.current_user = current_user
            
            # Update last login
            current_user.update_last_login()
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            logging.error(f"Token verification error: {str(e)}")
            return jsonify({'message': 'Token verification failed'}), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to ensure user has admin role."""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'message': 'Authentication required'}), 401
        
        if current_user.role != UserRole.ADMIN:
            return jsonify({'message': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated

def rate_limit(f):
    """Decorator to apply rate limiting to routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get client IP
        client_ip = request.remote_addr
        
        # Get current timestamp
        now = datetime.utcnow()
        
        # Check rate limit in Redis (to be implemented)
        # For now, just pass through
        return f(*args, **kwargs)
    return decorated 