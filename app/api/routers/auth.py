# app/api/routers/auth.py
from fastapi import APIRouter, Response, Cookie, Depends
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(request) -> AuthService:   # request: Request 타입 힌트 생략 가능
    return request.app.state.auth_service       # lifespan에서 주입한 싱글턴

@router.post("/login", response_model=TokenResponse)
async def login_endpoint(creds: LoginRequest, resp: Response, svc: AuthService = Depends(get_auth_service)):
    return await svc.login(creds, resp)

@router.post("/reissue", response_model=TokenResponse)
async def reissue_endpoint(
    resp: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
    svc: AuthService = Depends(get_auth_service),
):
    return await svc.reissue(resp, refresh_token)

@router.post("/logout")
async def logout_endpoint(
    resp: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
    svc: AuthService = Depends(get_auth_service),
):
    return await svc.logout(resp, refresh_token)
