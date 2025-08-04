# app/api/routers/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import create_user
from app.database import get_db
from app.models.user import User

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    user = create_user(db, user_in)
    return user
