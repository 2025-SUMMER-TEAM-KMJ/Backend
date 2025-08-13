from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class JobPostingBase(BaseModel):
    """채용 공고의 기본 정보를 담는 모델"""
    company_name: str = Field(..., description="회사명")
    job_title: str = Field(..., description="직무명")
    location: str = Field(..., description="근무 지역")
    job_group: str = Field(..., description="직군 (예: 개발, 기획, 디자인)")

class JobPostingResponse(JobPostingBase):
    """클라이언트에게 반환될 채용 공고 데이터 모델"""
    id: int
    created_at: datetime
    # 여기에 북마크 여부 등 개인화된 정보를 추가할 수 있음
    is_bookmarked: Optional[bool] = Field(None, description="현재 사용자의 북마크 여부 (로그인 시 제공)")

    class Config:
        orm_mode = True

class JobPostingListResponse(BaseModel):
    """채용 공고 목록과 전체 개수를 함께 반환하는 모델"""
    total: int = Field(..., description="조건에 맞는 전체 공고 수")
    items: List[JobPostingResponse] = Field(..., description="조회된 공고 목록")