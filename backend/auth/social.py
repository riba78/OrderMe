"""
Social Authentication Handler Module

This module manages social authentication integrations for the application:
1. Google OAuth2 authentication
2. Facebook authentication
3. JWT token generation and management

Features:
- Validates Google and Facebook OAuth tokens
- Handles user creation/retrieval for social logins
- Generates JWT tokens for authenticated sessions
- Manages token expiration and refresh

Configuration:
- Requires Google OAuth2 credentials
- Requires Facebook App credentials
- Uses JWT secret key for token signing

The module provides a unified interface for handling different social authentication
providers while maintaining consistent user session management.
"""

from typing import Optional, Dict
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
from datetime import datetime, timedelta

from models import User, db
from config import settings

class SocialAuthHandler:
    def __init__(self):
        self.google_client_id = settings.GOOGLE_CLIENT_ID
        self.facebook_app_id = settings.FACEBOOK_APP_ID
        self.facebook_app_secret = settings.FACEBOOK_APP_SECRET
        self.jwt_secret = settings.SECRET_KEY
        self.token_expire_days = settings.ACCESS_TOKEN_EXPIRE_DAYS

    def verify_google_token(self, token: str) -> Optional[Dict]:
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                self.google_client_id
            )

            # Check if the token is issued by Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return None

            return {
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', '')
            }
        except Exception as e:
            print(f"Google token verification error: {str(e)}")
            return None

    def verify_facebook_token(self, access_token: str, user_id: str) -> bool:
        try:
            # Verify the access token
            url = "https://graph.facebook.com/debug_token"
            params = {
                'input_token': access_token,
                'access_token': f"{self.facebook_app_id}|{self.facebook_app_secret}"
            }
            response = requests.get(url, params=params)
            data = response.json()

            if not data.get('data', {}).get('is_valid'):
                return False

            # Verify the user ID matches
            if str(data['data']['user_id']) != str(user_id):
                return False

            return True
        except Exception as e:
            print(f"Facebook token verification error: {str(e)}")
            return False

    def generate_token(self, user: User) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'sub': str(user.id),
            'email': user.email,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(days=self.token_expire_days)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    @staticmethod
    def create_or_get_user(user_data: dict) -> User:
        user = User.get_by_email(user_data['email'])
        if not user:
            user = User.create(
                email=user_data['email'],
                name=user_data.get('name', ''),
                provider=user_data['provider']
            )
        return user

    @staticmethod
    def create_token(user: User) -> str:
        expires_delta = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            'exp': expire,
            'sub': str(user.id),
            'email': user.email,
            'role': user.role.value
        }
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        ) 