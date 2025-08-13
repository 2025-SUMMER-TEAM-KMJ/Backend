from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from typing import List, Optional

# 스키마, 서비스, 인증 함수 임포트
from schemas.cover_letter_schemas import CoverLetterCreate, CoverLetterUpdate, CoverLetterResponse
from services.cover_letter_service import CoverLetterService, get_cover_letter_service
from security import get_current_user # 현재 유저 정보를 가져오는 의존성

# 라우터 설정: prefix와 tags를 사용해 URL을 그룹화하고 문서화
router = APIRouter(
    prefix="/cover-letters",
    tags=["Cover Letters"],
)

@router.post(
    "/",
    response_model=CoverLetterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="새로운 자기소개서 생성"
)
def create_cover_letter(
    request: CoverLetterCreate,
    service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: dict = Depends(get_current_user)
):
    """
    사용자의 프로필 또는 특정 채용 공고를 기반으로 새로운 자기소개서를 생성합니다.

    - **title**: 자기소개서의 제목 (5~100자)
    - **content**: 자기소개서의 내용 (10자 이상)
    - **type**: 'profile' 또는 'job_posting'
    - **job_posting_id**: type이 'job_posting'일 경우 필수
    """
    user_id = current_user.get("id") # 토큰에서 유저 ID 추출
    return service.create_cover_letter(user_id=user_id, request=request)

@router.get(
    "/",
    response_model=List[CoverLetterResponse],
    summary="자기소개서 목록 조회"
)
def get_cover_letters(
    type: Optional[Literal["profile", "job_posting"]] = Query(None, description="필터링할 자기소개서 타입"),
    offset: int = Query(0, ge=0, description="페이지네이션 시작점"),
    limit: int = Query(20, ge=1, le=100, description="한 번에 가져올 개수"),
    service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: dict = Depends(get_current_user)
):
    """
    현재 로그인된 사용자의 자기소개서 목록을 조건에 따라 조회합니다.
    `type` 쿼리 파라미터를 사용하여 특정 종류의 자기소개서만 필터링할 수 있습니다.
    """
    user_id = current_user.get("id")
    return service.get_all_cover_letters_by_user(user_id=user_id, type=type, offset=offset, limit=limit)

@router.get(
    "/{cover_letter_id}",
    response_model=CoverLetterResponse,
    summary="특정 자기소개서 상세 조회"
)
def get_cover_letter_detail(
    cover_letter_id: int = Path(..., gt=0, description="조회할 자기소개서의 고유 ID"),
    service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: dict = Depends(get_current_user)
):
    """
    ID를 사용하여 특정 자기소개서의 상세 내용을 조회합니다.
    본인이 작성한 자기소개서만 조회할 수 있습니다.
    """
    user_id = current_user.get("id")
    cover_letter = service.get_cover_letter_by_id(user_id=user_id, cover_letter_id=cover_letter_id)
    if not cover_letter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover letter not found")
    return cover_letter

@router.patch(
    "/{cover_letter_id}",
    response_model=CoverLetterResponse,
    summary="특정 자기소개서 수정"
)
def update_cover_letter(
    request: CoverLetterUpdate,
    cover_letter_id: int = Path(..., gt=0, description="수정할 자기소개서의 고유 ID"),
    service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: dict = Depends(get_current_user)
):
    """
    자기소개서의 제목 또는 내용을 수정합니다.
    변경하고 싶은 필드만 Request Body에 담아 보내면 됩니다.
    """
    user_id = current_user.get("id")
    return service.update_cover_letter(user_id=user_id, cover_letter_id=cover_letter_id, request=request)

@router.delete(
    "/{cover_letter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="특정 자기소개서 삭제"
)
def delete_cover_letter(
    cover_letter_id: int = Path(..., gt=0, description="삭제할 자기소개서의 고유 ID"),
    service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: dict = Depends(get_current_user)
):
    """
    ID를 사용하여 특정 자기소개서를 삭제합니다.
    성공 시 아무 내용도 반환하지 않습니다 (204 No Content).
    """
    user_id = current_user.get("id")
    service.delete_cover_letter(user_id=user_id, cover_letter_id=cover_letter_id)
    return None # 204 응답에는 바디가 없어야 함