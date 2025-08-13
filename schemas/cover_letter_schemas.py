from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime

# --- Domain 스키마 ---

# --- Request 스키마 ---

class CoverLetterCreate(BaseModel):
    """자기소개서 생성을 위한 Request Body 모델"""
    title: str = Field(..., min_length=5, max_length=100, description="자기소개서 제목")
    content: str = Field(..., min_length=10, description="자기소개서 내용")
    type: Literal["profile", "job_posting"] = Field(..., description="자기소개서 타입")
    job_posting_id: Optional[int] = Field(None, description="공고 기반 자소서일 경우, 해당 공고의 ID")

class CoverLetterUpdate(BaseModel):
    """자기소개서 수정을 위한 Request Body 모델 (모든 필드 선택적)"""
    title: Optional[str] = Field(None, min_length=5, max_length=100, description="자기소개서 제목")
    content: Optional[str] = Field(None, min_length=10, description="자기소개서 내용")


# --- Response 스키마 ---

class CoverLetterResponse(BaseModel):
    """클라이언트에게 반환될 자기소개서 데이터 모델"""
    id: int
    user_id: int
    title: str
    content: str
    type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # SQLAlchemy 모델과 호환되도록 설정