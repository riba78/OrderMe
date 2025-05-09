# business logic for user signup, signin, creating credentials and tokens.

from fastapi import HTTPException
from ..repositories.interfaces.user_repository import IUserRepository
from ..utils.security import hash_password, verify_password, create_access_token
from ..schemas.auth import Token
from ..schemas.admin_manager import AdminManagerCreate
from ..models.admin_manager import VerificationMethod

class AuthService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def signup(self, email: str, password: str) -> None:
        existing = await self.user_repo.find_by_email(email)
        if existing:
            print(f"[signup] Email already registered: {email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        creds = AdminManagerCreate(email=email, password=password, verification_method=VerificationMethod.email)
        #Hash password and store in AdminManager table
        hashed = hash_password(password)
        print(f"[signup] Creating user with email: {email}")
        await self.user_repo.create_user_with_credentials(creds)

    async def signin(self, email: str, password: str) -> Token:
        print(f"[signin] Attempting signin for email: {email}")
        user = await self.user_repo.find_by_email(email)
        print(f"[signin] User found: {user}")
        if not user:
            print(f"[signin] No user found for email: {email}")
        if user and hasattr(user, 'admin_manager'):
            print(f"[signin] user.admin_manager: {user.admin_manager}")
        if not user or not user.admin_manager:
            print(f"[signin] No user or admin_manager found for email: {email}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        try:
            if not verify_password(password, user.admin_manager.password_hash):
                print(f"[signin] Password verification failed for email: {email}")
                raise HTTPException(status_code=400, detail="Invalid credentials")
        except Exception as e:
            print(f"[signin] Exception during password verification for email: {email}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during password verification")
        token = create_access_token({"sub": user.id})
        print(f"[signin] Signin successful for email: {email}, token generated.")
        return Token(access_token=token, token_type="bearer")
    
    


