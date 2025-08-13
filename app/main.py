# app/main.py
from fastapi import FastAPI
from app.services.user import UserService
from app.api.routers import user

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # UserService 인스턴스 생성 후 앱 state에 저장
    app.state.user_service = UserService()

# 라우터 등록
app.include_router(user.router)
