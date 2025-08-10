# app/schemas/user.py
from pydantic import BaseModel, EmailStr, constr
from typing import Literal

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    name: str
    age: int
    gender: Literal["남성", "여성"]
    phone: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    age: int
    gender: str
    phone: str

