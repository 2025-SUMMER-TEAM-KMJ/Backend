from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from schemas.auth_schemas import UserCreate, Token
from schemas.user_schemas import UserProfileResponse
from services.user_service import UserService, get_user_service
from security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/signup",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입"
)
def signup(
    request: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    새로운 사용자를 생성합니다. 이메일은 고유해야 합니다.
    성공 시 생성된 사용자의 프로필 정보를 반환합니다.
    """
    return service.create_user(request=request)

@router.post("/signin", response_model=Token, summary="로그인 (토큰 발급)")
def signin(
    form_data: OAuth2PasswordRequestForm = Depends(), # 'username', 'password'를 form-data로 받음
    service: UserService = Depends(get_user_service)
):
    """
    사용자 이메일(form의 `username` 필드)과 비밀번호로 인증을 수행합니다.
    인증에 성공하면 JWT 액세스 토큰을 발급합니다.
    """
    user = service.authenticate_user(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 로그아웃은 구현 방식이 다양합니다. (토큰 블랙리스트, 클라이언트측 삭제 등)
# 여기서는 개념적인 엔드포인트만 제시합니다.
@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT, summary="로그아웃")
def signout(current_user: dict = Depends(get_current_user)):
    """
    로그아웃을 처리합니다.
    (서버 측 구현: 이 엔드포인트는 토큰을 받아 블랙리스트에 추가할 수 있습니다.)
    클라이언트는 이 API 호출 후 저장된 토큰을 삭제해야 합니다.
    """
    # 실제 구현: service.add_token_to_blacklist(token)
    return None