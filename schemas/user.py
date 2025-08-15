# app/schemas/user.py
from typing import Optional, List, Literal, Annotated, Mapping, Any
from pydantic import BaseModel, EmailStr, HttpUrl, Field

# 공통 타입
Password = Annotated[str, Field(min_length=8)]
YearMonth = Annotated[str, Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]

class SignUpRequest(BaseModel):
    email: EmailStr
    password: Password
    name: str
    age: int
    gender: Literal["남성", "여성"]
    phone: str

# 학력
class Education(BaseModel):
    school_name: str
    major: Optional[str] = None
    degree: Optional[Literal["Associate", "Bachelor", "Master", "Doctorate"]] = None
    start_date: YearMonth
    end_date: Optional[YearMonth] = None  # 재학 중이면 None

# 회사 경력
class WorkExperience(BaseModel):
    company_name: str
    job_group: str         # 직군
    job: str               # 직무
    start_date: YearMonth
    end_date: Optional[YearMonth] = None   # 재직 중이면 None
    description: Optional[str] = None

# 경험(프로젝트/대외활동 등)
class Experience(BaseModel):
    title: str
    description: Optional[str] = None
    link: Optional[HttpUrl] = None
    tech_stack: Optional[List[str]] = None
    start_date: Optional[YearMonth] = None
    end_date: Optional[YearMonth] = None

# 희망 포지션
class PreferredPosition(BaseModel):
    job_group: str
    job: Optional[str] = None

# 자격증
class Certification(BaseModel):
    name: str
    agency: Optional[str] = None
    issue_date: YearMonth

# QnA
class QnA(BaseModel):
    title: str
    content: Optional[str] = None
    category: Optional[str] = None

# 부분 업데이트용 (보낸 것만 반영)
class UserUpdateRequest(BaseModel):
    # 기본 정보
    age: Optional[int] = None
    phone: Optional[str] = None

    # URL
    urls: Optional[List[HttpUrl]] = None

    # 소개/역량/희망 포지션
    brief: Optional[str] = None
    competencies: Optional[List[str]] = None
    preferred_position: Optional[List[PreferredPosition]] = None

    # 학력/경력/경험/자격
    educations: Optional[List[Education]] = None
    work_experience: Optional[List[WorkExperience]] = None
    experiences: Optional[List[Experience]] = None
    certifications: Optional[List[Certification]] = None

    # QnA
    qnas: Optional[List[QnA]] = None

    # 관심 공고
    interest_jobs: Optional[List[str]] = None

class UserResponse(BaseModel):
    # 기본 정보
    email: EmailStr
    name: str
    age: int
    gender: Literal["남성", "여성"]
    phone: str

    # 링크/URL
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

    @classmethod
    def from_doc(cls, doc: Mapping[str, Any]) -> "UserResponse":
        return cls(
            email=doc["email"],
            name=doc["name"],
            age=doc["age"],
            gender=doc["gender"],
            phone=doc["phone"],

            urls=(doc.get("urls") or []),

            brief=doc.get("brief"),
            competencies=(doc.get("competencies") or []),
            preferred_position=(doc.get("preferred_position") or []),

            educations=(doc.get("educations") or []),
            work_experience=(doc.get("work_experience") or []),
            experiences=(doc.get("experiences") or []),
            certifications=(doc.get("certifications") or []),

            qnas=(doc.get("qnas") or []),

            interest_jobs=(doc.get("interest_jobs") or [])
        )
