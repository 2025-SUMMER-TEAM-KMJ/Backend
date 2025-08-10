# app/api/routers/user.py
from fastapi import APIRouter, Depends
from pymongo.collection import Collection
from app.database import get_collection
from app.schemas.user import UserCreate, UserResponse, ProfileUpdateRequest
from app.services.user import signup, update_profile
from app.deps.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    users_col: Collection = Depends(get_collection("users")),
):
    return signup(users_col, user_in)

@router.patch("/profile", response_model=UserResponse)
def patch_profile(
    payload: ProfileUpdateRequest,
    current_user=Depends(get_current_user),
    users_col: Collection = Depends(get_collection("users")),
):
    user_id = current_user["_id"]
    return update_profile(users_col, user_id, payload)