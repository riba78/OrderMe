# defines FastAPI routes for users operations; thin controllers delegate to 'UserService'.

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from ..services.user_service import UserService
from ..repositories.interfaces.user_repository import IUserRepository
from ..repositories.user_repository import UserRepository
from ..database import get_async_session
from ..dependencies.auth_dependencies import get_current_user
from ..models.user import User

#dependency injection functions
async def get_user_repository(session=Depends(get_async_session)) -> IUserRepository:
    return UserRepository(session)

async def get_user_service(repo: IUserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    """
    List all users with role-based access control.
    - Admins can see all users
    - Managers can only see their assigned customers
    - Other roles are forbidden
    """
    return await service.list_users(current_user)

@router.get("/managed-customers/", response_model=List[UserResponse])
async def list_managed_customers(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    """
    List customers managed by the current manager.
    - Only accessible by managers
    - Returns only customers assigned to the requesting manager
    """
    return await service.list_managed_customers(current_user)

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(get_current_user), 
    service: UserService = Depends(get_user_service)
    ) -> UserResponse:
    try:
        return await service.create_user(data, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))




