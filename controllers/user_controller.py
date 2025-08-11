from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.database import get_db
from app.services.user import signup

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(request: UserCreate, 
           service: UserService):
    pass

@router.post("/signin", response_model=UserResponse)
def signup(request: UserCreate, 
           service: UserService):
    pass

@router.post("/signup", response_model=UserResponse)
def logout(request: UserCreate, 
           service: UserService):
    pass


