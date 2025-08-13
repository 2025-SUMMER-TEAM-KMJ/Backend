# app/database.py
import os
import motor.motor_asyncio
from beanie import init_beanie
from pymongo import ASCENDING
from app.models.user_document import UserDocument
from app.models.refresh_token_document import RefreshTokenDocument
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "mydb")

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Beanie 초기화 (모든 Document 모델 등록)
    await init_beanie(
        database=db,
        document_models=[
            UserDocument,
            RefreshTokenDocument,
        ],
    )

    # TTL 인덱스 생성 (expires_at 기준)
    await db["refresh_tokens"].create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0,
        name="rt_expires_at_ttl",
        background=True,
    )

    return db
