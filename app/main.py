# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.user import UserService
from app.services.auth import AuthService
from app.api.routers import user, auth
from app.database import init_db

app = FastAPI()

'''
프론트엔드에서 API 호출 시 CORS 허용할 Origin(출처) 목록
- 여기 등록된 도메인에서만 브라우저가 쿠키/헤더를 포함해 요청 가능
- '*' 와일드카드 사용 시, 쿠키/인증 정보가 포함된 요청은 불가능 (보안상 위험)
- 개발 단계에서는 로컬 개발 서버 주소를 등록
- 프론트엔드 배포 후, 실제 서비스 도메인을 추가
- 프론트엔드 주소가 변경되면 반드시 여기도 업데이트 필요
- 예시:
  - 로컬: http://localhost:3000
  - 배포: https://your-frontend.com
'''
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # "https://your-production-domain.com" ex) 배포 도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # DB 초기화 + 클라이언트/DB 핸들 저장
    db, client = await init_db()
    app.state.mongo_client = client
    app.state.mongo_db = db

    app.state.user_service = UserService()
    app.state.auth_service = AuthService()

@app.on_event("shutdown")
async def shutdown_event():
    # Motor 커넥션풀 정리
    client = getattr(app.state, "mongo_client", None)
    if client:
        client.close()

# 라우터 등록
app.include_router(user.router)
app.include_router(auth.router)
