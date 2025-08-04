# app/services/user.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.crud.user import create_user as create_user_crud
from app.models.user import User

def signup(db: Session, user_in: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    return create_user_crud(db, user_in)
