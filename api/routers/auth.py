# app/api/routers/auth.py
from fastapi import APIRouter, Request, Response, Cookie, Depends
from schemas.auth import LoginRequest, TokenResponse
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service

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
