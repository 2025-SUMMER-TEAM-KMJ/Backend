# 파일: routers/user_router.py (사용자 정보 관련 엔드포인트 그룹)

from fastapi import APIRouter, Depends, Path, status

from schemas.user_schemas import UserProfileResponse, UserProfileUpdate
from services.user_service import UserService, get_user_service
from security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="현재 로그인된 사용자 프로필 수정"
)
def update_my_profile(
    request: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    현재 인증된 사용자의 프로필 정보(예: 사용자 이름)를 수정합니다.
    변경하고 싶은 필드만 Request Body에 담아 보내면 됩니다.
    """
    user_id = current_user.get("user_id")
    return service.update_user_profile(user_id=user_id, request=request)

@router.get(
    "/{user_id}/profile",
    response_model=UserProfileResponse,
    summary="특정 사용자 프로필 공개 조회"
)
def get_user_profile(
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    ID를 사용하여 다른 사용자의 공개 프로필을 조회합니다.
    (민감 정보가 제외된 프로필만 반환)
    """
    return service.get_user_by_id(user_id=user_id)