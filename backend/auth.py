from functools import wraps
from flask import request, jsonify, g
import jwt
from models import User
from config import Settings

settings = Settings()

def get_current_user():
    """Get the current user from the request context."""
    if not hasattr(g, 'current_user'):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            # Decode token
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get('sub')
            if user_id:
                g.current_user = User.query.get(user_id)
                return g.current_user
        except jwt.PyJWTError:
            return None
    
    return g.current_user

def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def create_access_token(user_id: int) -> str:
    """Create a new access token for a user."""
    from datetime import datetime, timedelta
    
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {
        'exp': expire,
        'sub': str(user_id)
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt 