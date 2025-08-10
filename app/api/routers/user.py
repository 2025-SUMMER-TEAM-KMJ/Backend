# app/api/routers/user.py
from fastapi import APIRouter, Depends
from pymongo.collection import Collection
from app.schemas.user import UserCreate, UserResponse
from app.database import get_collection
from app.services.user import signup

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    users_col: Collection = Depends(get_collection("users")),
):
    return signup(users_col, user_in)
