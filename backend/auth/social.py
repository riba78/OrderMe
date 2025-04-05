"""
Social Authentication Handler Module

This module manages social authentication integrations for the application:
1. Google OAuth2 authentication
2. Facebook authentication
3. JWT token generation and management
4. Verification methods
5. Activity logging

Features:
- Validates Google and Facebook OAuth tokens
- Handles user creation/retrieval for social logins
- Generates JWT tokens for authenticated sessions
- Manages token expiration and refresh
- Supports multiple verification methods
- Tracks authentication activities
- Implements rate limiting

Configuration:
- Requires Google OAuth2 credentials
- Requires Facebook App credentials
- Uses JWT secret key for token signing
- Configurable verification methods
- Activity logging settings

The module provides a unified interface for handling different social authentication
providers while maintaining consistent user session management.
"""

from typing import Optional, Dict
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
from datetime import datetime, timedelta
import logging

from models.user import User, UserRole, VerificationMethod
from models.user_verification_method import UserVerificationMethod
from models.activity_log import ActivityLog
from extensions import db
from config import settings
from .utils import log_activity

class SocialAuthHandler:
    def __init__(self):
        self.google_client_id = settings.GOOGLE_CLIENT_ID
        self.facebook_app_id = settings.FACEBOOK_APP_ID
        self.facebook_app_secret = settings.FACEBOOK_APP_SECRET

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

            # Log verification attempt
            log_activity(
                user_id=None,
                activity_type='google_token_verification',
                metadata={'status': 'success', 'email': idinfo['email']}
            )

            return {
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', '')
            }
        except Exception as e:
            logging.error(f"Google token verification error: {str(e)}")
            # Log failed verification
            log_activity(
                user_id=None,
                activity_type='google_token_verification',
                metadata={'status': 'failed', 'error': str(e)}
            )
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
                # Log failed verification
                log_activity(
                    user_id=None,
                    activity_type='facebook_token_verification',
                    metadata={'status': 'failed', 'reason': 'invalid_token'}
                )
                return False

            # Verify the user ID matches
            if str(data['data']['user_id']) != str(user_id):
                # Log failed verification
                log_activity(
                    user_id=None,
                    activity_type='facebook_token_verification',
                    metadata={'status': 'failed', 'reason': 'user_id_mismatch'}
                )
                return False

            # Log successful verification
            log_activity(
                user_id=None,
                activity_type='facebook_token_verification',
                metadata={'status': 'success', 'user_id': user_id}
            )

            return True
        except Exception as e:
            logging.error(f"Facebook token verification error: {str(e)}")
            # Log failed verification
            log_activity(
                user_id=None,
                activity_type='facebook_token_verification',
                metadata={'status': 'failed', 'error': str(e)}
            )
            return False

    def generate_token(self, user: User) -> str:
        """Generate JWT token for authenticated user"""
        expires_delta = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            'exp': expire,
            'sub': str(user.id),
            'email': user.email,
            'role': user.role.value
        }
        return jwt.encode(
            payload, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )

    def create_or_get_user(self, user_data: dict) -> User:
        """Create or get user with social authentication"""
        try:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                # Create new user
                user = User(
                    email=user_data['email'],
                    name=user_data.get('name', ''),
                    role=UserRole.USER,
                    is_verified=True,
                    is_active=True,
                    primary_verification_method=VerificationMethod.GOOGLE if user_data['provider'] == 'google' else VerificationMethod.FACEBOOK
                )
                db.session.add(user)
                db.session.commit()

                # Create verification method record
                verification = UserVerificationMethod(
                    user_id=user.id,
                    method_type=VerificationMethod.GOOGLE if user_data['provider'] == 'google' else VerificationMethod.FACEBOOK,
                    identifier=user_data['email'],
                    is_verified=True
                )
                db.session.add(verification)
                db.session.commit()

                # Log user creation
                log_activity(
                    user_id=user.id,
                    activity_type='social_user_creation',
                    metadata={
                        'provider': user_data['provider'],
                        'email': user_data['email']
                    }
                )

            return user
        except Exception as e:
            logging.error(f"Error creating/getting user: {str(e)}")
            raise 