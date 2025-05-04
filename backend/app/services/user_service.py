# service handling business logic and role-based permission checks for users.

from fastapi import HTTPException
from typing import List
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserUpdate
from ..repositories.interfaces.user_repository import IUserRepository
from .crud_service import CRUDService

class UserService(CRUDService[User, UserCreate, UserUpdate]):
    """Contains business rules for creating, updating and deleting users."""

    def __init__(self, repository: IUserRepository):
        super().__init__(repository) 

    async def create_user(self, user_data: UserCreate, current_user: User) -> User:
        """
        Create a new user.

        - Only admins and managers can create users.
        - Managers can only create customers assigned to themselves.
        """
        # Only admins and managers can create users
        if current_user.role not in [UserRole.admin, UserRole.manager]:
            raise HTTPException(status_code=403, detail="Not authorized to create users")
        # Managers can only create customers assigned to themselves
        if (
            current_user.role == UserRole.manager and
            user_data.role != UserRole.customer
        ):
            raise HTTPException(status_code=403, detail="Managers can only create customers")
        return await self.create(user_data)
    
    async def get_user(self, id: str, current_user: User) -> User:
        """
        Retrieve a user by ID with access control.

        - Admins may view any user.
        - Managers can only view users they manage.
        - All other roles are forbidden from viewing users.
        """
        user = await self.get(id)
        # Admins may view any user
        if current_user.role == UserRole.admin:
            return user
        # Managers can only view users they manage
        if (
            current_user.role == UserRole.manager and
            user.admin_manager and
            user.admin_manager.id == current_user.id
        ):
            return user
        # All other roles are forbidden
        raise HTTPException(status_code=403, detail="Not authorized to view this user")
    
    async def update_user(self, id: str, data: UserUpdate, current_user: User) -> User:
        """
        Update a user by ID with access control.

        - Admins may update any user.
        - Managers may update only customers assigned to them.
        - All other roles cannot update any user.
        """
        user = await self.get(id)
        # Admins may update any user
        if current_user.role == UserRole.admin:
            return await self.update(id, data)
        # Managers may update only customers assigned to them
        if (
            current_user.role == UserRole.manager and
            user.role == UserRole.customer and
            user.admin_manager and
            user.admin_manager.id == current_user.id
        ):
            return await self.update(id, data)
        # All other roles cannot update any user
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    async def delete_user(self, id: str, current_user: User) -> None:
        """
        Delete a user by ID with role-based access control.

        - Admins can delete any user.
        - Managers can delete customers assigned to them.
        - All others are forbidden.
        """
        user = await self.get(id)
        # Admins can delete any user
        if current_user.role == UserRole.admin:
            return await self.delete(id)
        # Managers can delete customers assigned to them
        if (
            current_user.role == UserRole.manager and
            user.role == UserRole.customer and
            user.admin_manager and
            user.admin_manager.id == current_user.id
        ):
            return await self.delete(id)
        # Otherwise, forbidden
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    
    async def toggle_activation(self, id: str, activate: bool, current_user: User) -> User:
        """
        Toggle the activation status of a user by ID with access control.

        - Admins may toggle activation for any user.
        - Managers may toggle activation only for customers assigned to them.
        - All other roles cannot toggle activation for any user.
        """
        user = await self.get(id)
        # Admins may toggle activation for any user
        if current_user.role == UserRole.admin:
            return await self.update(id, UserUpdate(is_active=activate))
        # Managers may toggle activation only for customers assigned to them
        if (
            current_user.role == UserRole.manager and
            user.role == UserRole.customer and
            user.admin_manager and
            user.admin_manager.id == current_user.id
        ):
            return await self.update(id, UserUpdate(is_active=activate))
        # All other roles cannot toggle activation
        raise HTTPException(status_code=403, detail="Not authorized to toggle activation for this user")
    
    async def list_users(self, current_user: User) -> List[User]:
        """
        List users with role-based access control.

        - Admins can see all users
        - Managers can only see their assigned customers
        - Other roles are forbidden
        """
        # Admins can see all users
        if current_user.role == UserRole.admin:
            return await self.list_all()
        
        # Managers can only see their assigned customers
        if current_user.role == UserRole.manager:
            users = await self.list_all()
            return [
                user for user in users 
                if user.role == UserRole.customer and 
                user.admin_manager and 
                user.admin_manager.id == current_user.id
            ]
        
        # Other roles are forbidden
        raise HTTPException(
            status_code=403,
            detail="Not authorized to list users"
        )
    
    async def list_managed_customers(self, current_user: User) -> List[User]:
        """
        List customers managed by the current manager.
        
        Args:
            current_user: The manager requesting their customers
            
        Returns:
            List[User]: List of customers assigned to the manager
            
        Raises:
            HTTPException: If the user is not a manager
        """
        if current_user.role != UserRole.manager:
            raise HTTPException(
                status_code=403,
                detail="Only managers can access their managed customers"
            )

        users = await self.list_all()
        return [
            user for user in users 
            if user.role == UserRole.customer and 
            user.admin_manager and 
            user.admin_manager.id == current_user.id
        ]
    
    