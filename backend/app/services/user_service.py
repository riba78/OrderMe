"""
User Service Module

This module defines the UserService class that handles business logic
for user-related operations including:
- User creation and management
- User authentication
- User role management
- User status management
- User profile updates

It provides a layer of business logic between the controllers
and repositories for user-related operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repository.get_by_email(email)

    def get_users(self) -> List[User]:
        return self.user_repository.get_all()

    def create_user(self, user_data: UserCreate) -> User:
        user_dict = {
            "email": user_data.email,
            "hashed_password": user_data.password,  # Note: Password should be hashed before this
            "role": user_data.role
        }
        return self.user_repository.create(user_dict)

    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        user = self.user_repository.get_by_id(user_id)
        if user:
            data = user_data.dict(exclude_unset=True)
            return self.user_repository.update(user_id, data)
        return None

    def delete_user(self, user_id: str) -> bool:
        return self.user_repository.delete(user_id)

    def get_active_users(self) -> List[User]:
        return self.user_repository.get_active_users()

    def get_users_by_role(self, role: str) -> List[User]:
        return self.user_repository.get_users_by_role(role) 