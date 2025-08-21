# app/schemas/job_posting.py
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from datetime import datetime

class JobPostingMetadata(BaseModel):
    source: Optional[str] = None
    sourceUrl: Optional[HttpUrl] = None
    crawledAt: Optional[datetime] = None

class JobPostingCompanyAddress(BaseModel):
    country: Optional[str] = None
    location: Optional[str] = None
    district: Optional[str] = None
    full_location: Optional[str] = None

class JobPostingCompany(BaseModel):
    name: str
    logo_img: Optional[str] = None
    address: Optional[JobPostingCompanyAddress] = None
    features: List[str] = Field(default_factory=list)
    avgSalary: Optional[int] = None
    avgEntrySalary: Optional[int] = None

class JobPostingPosition(BaseModel):
    jobGroup: Optional[str] = None
    job: List[str] = Field(default_factory=list)

class JobPostingDetail(BaseModel):
    position: Optional[JobPostingPosition] = None
    intro: Optional[str] = None
    main_tasks: Optional[str] = None
    requirements: Optional[str] = None
    preferred_points: Optional[str] = None
    benefits: Optional[str] = None
    hire_rounds: Optional[str] = None

class JobPostingResponse(BaseModel):
    # 로그인 안 한 사용자는 bookmarked를 응답에서 아예 제외해야 하므로
    # FastAPI 라우터에서 response_model_exclude_none=True 를 사용합니다.
    model_config = ConfigDict(from_attributes=True)

    id: str
    metadata: JobPostingMetadata
    company: JobPostingCompany
    detail: JobPostingDetail

    due_time: Optional[datetime] = None

    externalUrl: Optional[HttpUrl] = None
    skill_tags: List[str] = Field(default_factory=list)
    sourceData: Optional[str] = None
    status: Optional[Literal["active", "inactive", "closed"]] = "active"
    title_images: List[str] = Field(default_factory=list)
    
    bucket: Optional[str] = None
    salary_bucket_2m_label: Optional[str] = None

    # 로그인 사용자의 경우에만 True/False를 채워줌. 비로그인 시 None → 라우터에서 exclude_none 처리.
    bookmarked: Optional[bool] = None

    @classmethod
    def from_doc(cls, doc) -> "JobPostingResponse":
        """Beanie Document 객체를 Pydantic 스키마 객체로 변환합니다."""
        d = doc.model_dump()
        
        # _id (ObjectId)를 id (str)로 변환
        d["id"] = str(doc.id)
        
        return cls(**d)

class JobPostingListResponse(BaseModel):
    """채용 공고 목록과 전체 개수를 함께 반환하는 모델"""
    total: int = Field(..., description="조건에 맞는 전체 공고 수")
    items: List[JobPostingResponse] = Field(..., description="조회된 공고 목록")