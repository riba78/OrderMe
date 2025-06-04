# service handling business logic and role-based permission checks for users.

from fastapi import HTTPException
from typing import List
from uuid import UUID
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..repositories.interfaces.user_repository import IUserRepository
from .crud_service import CRUDService
import logging # Temporary import for debugging

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
    
    async def list_users(self, current_user: User) -> List[UserResponse]:
        """
        List users with role-based access control.

        - Admins can see all users
        - Managers can only see their assigned customers
        - Other roles are forbidden
        """
        # Admins can see all users
        if current_user.role == UserRole.admin:
            users = await self.list_all()
        # Managers can only see their assigned customers
        elif current_user.role == UserRole.manager:
            users = await self.list_all()
            users = [
                user for user in users 
                if user.role == UserRole.customer and 
                user.admin_manager and 
                user.admin_manager.id == current_user.id
            ]
        else:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to list users"
            )
        user_responses = []
        for user in users:
            admin_manager = user.admin_manager
            customer = user.customer if hasattr(user, 'customer') else None
            # For admin/manager: set email, for customer: set phone
            email = admin_manager.email if admin_manager and admin_manager.email else None
            phone = customer.phone if customer and customer.phone else None
            user_responses.append(UserResponse(
                id=user.id,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                email=email,
                phone=phone
            ))
        return user_responses
    
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

    async def update_user_with_permissions(
        self,
        user_id_to_update: UUID,
        update_data: UserUpdate,
        requesting_user: User
    ) -> User:
        """
        Update a user's details with role-based authorization.
        - Admins can update any user's email, phone, role, and status.
        - Managers can update email, phone, and status of their assigned customers only.
          (Managers cannot change user roles).
        """
        logging.warning(f"UserService: Attempting to update user with ID: {user_id_to_update}, type: {type(user_id_to_update)}") # Temporary log

        target_user = await self.repository.get_by_id(user_id_to_update)
        logging.warning(f"UserService: User found by repository: {target_user}") # Temporary log

        if not target_user:
            raise ValueError("User to update not found")

        if requesting_user.role == UserRole.admin:
            # Admins can update any field present in UserUpdate schema
            # The super().update method will handle model_dump(exclude_unset=True)
            # if it's designed to take Pydantic models.
            updated_user = await super().update(id=user_id_to_update, data=update_data)
            return updated_user

        elif requesting_user.role == UserRole.manager:
            if target_user.role != UserRole.customer:
                raise PermissionError("Managers can only update customer users.")

            # Check if the customer is assigned to this manager
            if not target_user.admin_manager or target_user.admin_manager.id != requesting_user.id:
                raise PermissionError("Managers can only update customers specifically assigned to them.")

            if update_data.role is not None:
                # Managers are not allowed to change roles at all.
                raise PermissionError("Managers cannot change user roles.")

            # Managers can only update email, phone, and is_active status
            manager_allowed_fields = {}
            if update_data.email is not None:
                manager_allowed_fields['email'] = update_data.email
            if update_data.phone is not None:
                manager_allowed_fields['phone'] = update_data.phone
            if update_data.is_active is not None:
                manager_allowed_fields['is_active'] = update_data.is_active
            
            if not manager_allowed_fields:
                # No fields provided that a manager is allowed to update.
                # (e.g., payload was empty or only contained 'role')
                # We return the target user as is, as no valid update operation can be performed.
                return target_user

            manager_safe_update_data = UserUpdate(**manager_allowed_fields)
            updated_user = await super().update(id=user_id_to_update, data=manager_safe_update_data)
            return updated_user
        
        else: # Other roles (e.g., customer, or any other defined role)
            raise PermissionError("You do not have permission to update this user's details.")
    
    