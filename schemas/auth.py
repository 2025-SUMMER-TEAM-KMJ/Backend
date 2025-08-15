# app/schemas/auth.py
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field

Password = Annotated[str, Field(min_length=8)]

class LoginRequest(BaseModel):
    email: EmailStr
    password: Password

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
