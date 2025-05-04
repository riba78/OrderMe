# pydantic schema for authentication request and token responses.

from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

class UserSignUp(BaseModel):
    email: EmailStr
    password: str

class UserSignIn(BaseModel):
    email: EmailStr
    password: str


