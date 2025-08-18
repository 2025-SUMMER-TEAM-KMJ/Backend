# api/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from schemas.user import SignUpRequest, UserUpdateRequest, UserResponse
from deps.auth import get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])

# 앱 state에서 서비스 꺼내는 의존성
def get_user_service(request: Request):
    return request.app.state.user_service

# 회원가입: POST /users/signup
@router.post("/signup",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
             summary="회원가입"
)
async def sign_up(req: SignUpRequest, svc=Depends(get_user_service)):
    try:
        return await svc.sign_up(req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# 내 프로필 조회: GET /users
@router.get("",
            response_model=UserResponse,
            summary="프로필 조회",
            description="응답에는 프로필 사진의 GCS object key(`profile_img_key`)만 포함됩니다.\n"
                        "이미지 파일은 `<img src=\"/users/profile-image\">`처럼 다운로드 API 경로로 직접 표시해야 합니다.\n"
                        "프로필 사진이 없을 수 있으니 키 존재 여부를 항상 확인해야 합니다."
)
async def get_profile(user_id: str = Depends(get_current_user_id), svc=Depends(get_user_service)):
    try:
        return await svc.get_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# 내 프로필 부분 업데이트: PATCH /users
@router.patch("", response_model=UserResponse)
async def update_profile(
    req: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    svc=Depends(get_user_service)
):
    try:
        return await svc.update_profile(user_id, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# 프로필 사진 업로드
@router.post(
    "/profile-image",
    status_code=status.HTTP_201_CREATED,
    summary="프로필 이미지 업로드",
    description=(
        "요청 바디에 이미지 파일 바이트를 그대로 넣어야 합니다. 헤더에는 Content-Type을 설정해야 합니다.\n"
        "Content-Type은 image/png, image/jpeg, image/jpg 중 하나로 설정해야 합니다."
    )
)
async def upload_profile_image(request: Request, user_id: str = Depends(get_current_user_id), svc=Depends(get_user_service)):
    raw = await request.body()
    content_type = request.headers.get("Content-Type", "")
    try:
        metadata = await svc.upload_profile_image(raw, user_id, content_type)
        return metadata
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="업로드에 실패하였습니다.")

@router.get(
    "/profile-image",
    summary="프로필 이미지 다운로드(표시용)",
    responses={
        200: {"content": {"image/*": {}}},
        404: {"description": "이미지 없음"},
    },
    description=(
        "프론트 예시:\n"
        "```html\n"
        "<img src=\"/users/profile-image\" alt=\"profile\" />\n"
        "```\n"
        "백엔드가 GCS에서 파일을 읽어 응답 바디에 이미지 바이트로 내려줍니다."
    )
)
async def download_profile_image(user_id: str = Depends(get_current_user_id), svc=Depends(get_user_service)):
    try:
        data, content_type, filename = await svc.download_profile_image(user_id)
        return Response(
            content=data,
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{filename}"',
                "Cache-Control": "public, max-age=31536000, immutable",
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete(
    "/profile-image",
    summary="프로필 이미지 삭제",
    description="현재 로그인 사용자의 프로필 이미지를 GCS와 DB에서 삭제합니다."
)
async def delete_profile_image(user_id: str = Depends(get_current_user_id), svc=Depends(get_user_service)):
    try:
        return await svc.delete_profile_image(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="이미지 삭제를 실패하였습니다.")
