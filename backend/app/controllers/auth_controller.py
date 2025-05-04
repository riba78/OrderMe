# FastAPI routes for signup and singin endpoints, delegating to 'AuthService'.

from fastapi import APIRouter, Depends
from ..schemas.auth import UserSignUp, UserSignIn, Token
from ..services.auth_service import AuthService
from ..repositories.user_repository import UserRepository
from ..database import get_async_session
from ..schemas.user import UserResponse
from ..models.user import User
from ..dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_auth_service(session=Depends(get_async_session)) -> AuthService:
    repo = UserRepository(session)
    return AuthService(repo)

@router.post("/signup", status_code=201)
async def signup(
    data: UserSignUp,
    service: AuthService = Depends(get_auth_service)
):
    await service.signup(data.email, data.password)
    return {"detail": "User created successfully"}

@router.post("/signin", response_model=Token)
async def signin(
    data: UserSignIn,
    service: AuthService = Depends(get_auth_service)
) -> Token:
    return await service.signin(data.email, data.password)





