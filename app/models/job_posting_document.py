# app/models/job_posting_document.py
from typing import Any, Dict, List, Optional
from datetime import datetime
from beanie import Document, Indexed
from pydantic import BaseModel, Field

# 회사 주소
class CompanyAddress(BaseModel):
    country: Optional[str] = None
    location: Optional[str] = None
    district: Optional[str] = None
    full_location: Optional[str] = None

# 회사 정보
class Company(BaseModel):
    name: str
    logo_img: Optional[str] = None
    address: Optional[CompanyAddress] = None

# 직무
class Position(BaseModel):
    jobGroup: Optional[str] = None
    job: Optional[str] = None

# 상세 정보
class Detail(BaseModel):
    position: Optional[Position] = None
    intro: Optional[str] = None
    main_tasks: Optional[str] = None
    requirements: Optional[str] = None
    preferred_points: Optional[str] = None
    benefits: Optional[str] = None
    hire_rounds: Optional[str] = None

# 메타데이터
class Metadata(BaseModel):
    source: Optional[str] = None
    sourceUrl: Optional[str] = None
    crawledAt: Optional[datetime] = None

class JobPostingDocument(Document):
    metadata: Metadata
    company: Company
    detail: Detail

    externalUrl: Optional[str] = None
    skill_tags: List[str] = Field(default_factory=list)
    sourceData: Optional[str] = None
    status: Optional[str] = "active"
    title_images: List[str] = Field(default_factory=list)

    class Settings:
        name = "wanted_job_postings"  # 컬렉션명
        # 크롤링 중복 방지용
        indexes = [
            Indexed("metadata.sourceUrl", unique=True),
            Indexed("status"),
            Indexed("company.name"),
            Indexed("detail.position.jobGroup"),
            Indexed("detail.position.job"),
        ]
