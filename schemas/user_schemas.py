from pydantic import BaseModel, Field
from typing import Optional

class UserProfileResponse(BaseModel):
    """사용자 프로필 조회 시 반환하는 모델 (비밀번호 등 민감 정보 제외)"""
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class UserProfileUpdate(BaseModel):
    """사용자 프로필 수정 시 사용하는 모델"""
    username: Optional[str] = Field(None, min_length=2)
    # 필요하다면 다른 필드 추가 (예: bio, profile_image_url)