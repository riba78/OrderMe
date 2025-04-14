"""
User Controller Module

This module handles all user-related endpoints including:
- User profile management
- User role management
- User status management
- User list and search functionality

It provides CRUD operations for users and includes role-based
access control for different user operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.models.models import User, UserRole
from app.database import get_db
from app.controllers.auth_controller import get_current_user
from ..services.user_service import UserService
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..dependencies import get_user_service

router = APIRouter()

# Pydantic models
class UserProfile(BaseModel):
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    role: UserRole
    is_active: bool

    class Config:
        orm_mode = True

# Endpoints
@router.get("/test")
async def test_user():
    """Test endpoint to verify the user controller is working"""
    return {"message": "User controller is working"}

@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    user = db.query(User).filter(User.id == current_user["id"]).first()
    return user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    profile: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    user = db.query(User).filter(User.id == current_user["id"]).first()
    
    # Update only provided fields
    for key, value in profile.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user by ID (admin only)"""
    if current_user["role"] != UserRole.ADMIN and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's information"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/", response_model=List[UserResponse])
def get_users(user_service: UserService = Depends(get_user_service)):
    return user_service.get_users()

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    updated_user = user_service.update_user(user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/users/{user_id}")
def delete_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    try:
        success = user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/role/{role}", response_model=List[UserResponse])
def get_users_by_role(role: UserRole, user_service: UserService = Depends(get_user_service)):
    return user_service.get_users_by_role(role)

@router.put("/{user_id}/activate", response_model=UserResponse)
async def toggle_user_activation(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Activate or deactivate a user (admin only)"""
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify user status"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user 