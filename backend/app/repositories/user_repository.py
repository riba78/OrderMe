"""
User Repository Module

This module defines the UserRepository class that handles database operations
for the User model including:
- User-specific queries
- User role management
- User status management

It extends the BaseRepository and provides specialized methods
for user-related database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.user import User, UserRole, AdminManager
from .base_repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return self.session.query(User).filter(User.is_active == True).all()

    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get users by role."""
        return self.session.query(User).filter(User._role == role.value).all()
        
    def get_admin_by_email(self, email: str) -> Optional[AdminManager]:
        """Get admin or manager by email address."""
        return self.session.query(AdminManager).filter(AdminManager.email == email).first()
        
    def get_admin_with_user(self, email: str) -> Optional[tuple]:
        """Get admin or manager with associated user by email address."""
        admin = self.session.query(AdminManager).filter(AdminManager.email == email).first()
        if admin:
            user = self.session.query(User).filter(User.id == admin.user_id).first()
            return admin, user
        return None 