from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.user import UserService
from services.auth import AuthService
from api.routers import user, cover_letter, auth, job_posting
from database import init_db



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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    # Mongo/Motor + Beanie 초기화
    db, client = await init_db()
    app.state.mongo_client = client
    app.state.mongo_db = db

    # 서비스 인스턴스 준비(필요한 것만)
    app.state.user_service = UserService()
    app.state.auth_service = AuthService()

    yield

    # --- shutdown ---
    client = getattr(app.state, "mongo_client", None)
    if client:
        client.close()


app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # ← 쿠키/인증 헤더 허용
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(job_posting.router)
app.include_router(cover_letter.router)
