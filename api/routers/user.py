# app/api/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.user import SignUpRequest, UserUpdateRequest, UserResponse
from deps.auth import get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])

# 앱 state에서 서비스 꺼내는 의존성
def get_user_service(request: Request):
    return request.state.user_service

# 회원가입: POST /users/signup
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(req: SignUpRequest, svc=Depends(get_user_service)):
    try:
        return await svc.sign_up(req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# 내 프로필 조회: GET /users
@router.get("", response_model=UserResponse)
async def get_profile(user_id: str = Depends(get_current_user_id), svc=Depends(get_user_service)):
    try:
        return await svc.get_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# 내 프로필 부분 업데이트: PATCH /users
@router.patch("", response_model=UserResponse)
async def update_profile(
    req: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    svc=Depends(get_user_service)
):
    try:
        return await svc.update_profile(user_id, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
