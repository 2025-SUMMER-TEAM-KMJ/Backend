# app/models/user_document.py
from beanie import Document, Indexed
from pydantic import EmailStr, HttpUrl, Field
from typing import List, Optional, Literal

# API 스키마 재사용
from schemas.user import (
    Education, WorkExperience, Experience, PreferredPosition,
    Certification, QnA
)

class UserDocument(Document):
    # 기본 정보
    email: Indexed(EmailStr, unique=True)  # 이메일 유니크 인덱스
    password: str
    name: str
    age: int
    gender: Literal["남성", "여성"]
    phone: str

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
