# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import user, auth
from app.database import init_indexes

app = FastAPI()

# CORS — 리프레시 토큰 쿠키 쓰기 때문에 credentials 허용해야 함
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트 주소로 교체 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Mongo 인덱스(이메일 unique, refresh TTL 등) 1회 생성
    init_indexes()

app.include_router(user.router)
app.include_router(auth.router)
