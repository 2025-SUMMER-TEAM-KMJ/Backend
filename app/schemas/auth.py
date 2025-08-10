# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, constr

class LoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
