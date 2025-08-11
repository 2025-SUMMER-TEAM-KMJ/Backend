# app/main.py
from fastapi import FastAPI
from app.api.routers import user

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
