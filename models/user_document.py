# models/user_document.py
from beanie import Document, Indexed
from pydantic import EmailStr, HttpUrl, Field
from typing import List, Optional, Literal

# API 스키마 재사용
from schemas.user import (
    Education, WorkExperience, Experience, PreferredPosition,
    Certification, QnA
)


"""
전체적으로 수정 필요. Object ID는 그대로 두고 따로 UUID를 부여해서 관리하는 방향으로 수정. 다른 스키마도 같은 형식으로 구성 필요
그리고 이미지도 저장해야 하기 때문에 그 부분도 추가 필요
"""

class UserDocument(Document):
    # 기본 정보
    email: Indexed(EmailStr, unique=True)  # 이메일 유니크 인덱스
    password: str
    name: str
    age: int
    gender: Literal["남성", "여성"]
    phone: str

    # 프로필 이미지, object key만 저장
    profile_img: Optional[str] = None

    # URL
    urls: List[HttpUrl] = Field(default_factory=list)

    # 소개/역량/희망 포지션
    brief: Optional[str] = None
    competencies: List[str] = Field(default_factory=list)
    preferred_position: List[PreferredPosition] = Field(default_factory=list)

    # 학력/경력/경험/자격
    educations: List[Education] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)

    # QnA
    qnas: List[QnA] = Field(default_factory=list)

    # 관심 공고
    interest_jobs: List[str] = Field(default_factory=list)

    class Settings:
        # MongoDB 컬렉션명 -> 정확한 명칭으로 수정 필요
        name = "users"
