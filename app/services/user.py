# app/services/user.py
from fastapi import HTTPException
from pymongo.collection import Collection
from app.schemas.user import UserCreate
from app.crud.user import create_user as create_user_crud, get_user_by_email

def signup(users_col: Collection, user_in: UserCreate):
    if get_user_by_email(users_col, user_in.email):
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    try:
        return create_user_crud(users_col, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))