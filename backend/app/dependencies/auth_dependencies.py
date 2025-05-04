# backend/app/dependencies/auth_dependencies.py

"""
Authentication-related FastAPI dependencies.

Key Features:
- Provides a dependency to extract and validate the current user from a JWT token.
- Uses OAuth2 Bearer token scheme for authentication.
- Handles token decoding, validation, and user lookup.
- Raises HTTP 401 errors for invalid or missing credentials.

Usage:
    from ..dependencies.auth_dependencies import get_current_user

    @router.get("/me")
    async def read_current_user(current_user: User = Depends(get_current_user)):
        return current_user
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from ..utils.security import decode_access_token
from ..repositories.user_repository import UserRepository
from ..database import get_async_session
from ..models.user import User

# OAuth2 scheme for extracting the Bearer token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

# Dependency to get a UserRepository instance with an async DB session
async def get_user_repository(session=Depends(get_async_session)) -> UserRepository:
    return UserRepository(session)

# Dependency to get the current authenticated user from the JWT token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Dependency to get the current authenticated user from the JWT token.
    Raises HTTP 401 if the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token to get the payload
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Look up the user in the database
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user