from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional

# 스키마, 서비스, 인증 함수 임포트
from schemas.job_posting_schemas import JobPostingResponse, JobPostingListResponse
from services.job_posting_service import JobPostingService, get_job_posting_service
from security import get_current_user, get_optional_current_user


# 라우터 설정
router = APIRouter(
    prefix="/job-postings",
    tags=["Job Postings"],
)

@router.get(
    "/{id}",
    response_model=JobPostingListResponse,
    summary="채용 공고 목록 조회 (공개)",
)
def get_job_posting(
    id: str,
    service: JobPostingService = Depends(get_job_posting_service),
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    """
    다양한 필터 조건에 따라 채용 공고 목록을 조회합니다.
    **이 엔드포인트는 로그인을 하지 않아도 접근 가능합니다.**

    - 로그인 상태일 경우, 각 공고의 북마크 여부(`is_bookmarked`) 정보가 함께 제공됩니다.
    """
    user_id = current_user.get("id") if current_user else None
    return service.get_filtered_job_postings()

@router.get(
    "/",
    response_model=JobPostingListResponse,
    summary="채용 공고 목록 조회 (공개)",
)
def get_job_postings(
    query: Optional[str] = Query(None),
    job_group: Optional[str] = Query(None, description="필터링할 직군"),
    job: Optional[str] = Query(None, description="필터링할 직무"),
    location: Optional[str] = Query(None, description="필터링할 근무 지역"),
    offset: int = Query(0, ge=0, description="페이지네이션 시작점"),
    limit: int = Query(20, ge=1, le=100, description="한 번에 가져올 개수"),
    service: JobPostingService = Depends(get_job_posting_service),
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    """
    다양한 필터 조건에 따라 채용 공고 목록을 조회합니다.
    **이 엔드포인트는 로그인을 하지 않아도 접근 가능합니다.**

    - 로그인 상태일 경우, 각 공고의 북마크 여부(`is_bookmarked`) 정보가 함께 제공됩니다.
    """
    user_id = current_user.get("id") if current_user else None
    return service.get_filtered_job_postings(
        user_id=user_id, job_group=job_group, job=job, location=location,
        offset=offset, limit=limit
    )

@router.get(
    "/recommendations",
    response_model=JobPostingListResponse,
    summary="사용자 맞춤 채용 공고 추천"
)
def recommend_job_postings(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: JobPostingService = Depends(get_job_posting_service),
    current_user: dict = Depends(get_current_user)
):
    """
    현재 로그인된 사용자의 프로필, 활동 기록 등을 기반으로
    가장 적합한 채용 공고를 추천합니다.
    """
    user_id = current_user.get("id")
    return service.get_recommended_job_postings(user_id=user_id, offset=offset, limit=limit)

