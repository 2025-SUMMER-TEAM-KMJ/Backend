# app/database.py
import os
import motor.motor_asyncio
from beanie import init_beanie
from app.models.user_document import UserDocument
from app.models.refresh_token_document import RefreshTokenDocument
from app.models.job_posting_document import JobPostingDocument
from app.models.user_job_bookmark_document import UserJobBookmarkDocument
from app.models.cover_letter_document import CoverLetterDocument
from settings import MONGO_URI, DB_NAME

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Beanie 초기화 (모든 Document 모델 등록)
    await init_beanie(
        database=db,
        document_models=[
            UserDocument,
            RefreshTokenDocument,
            JobPostingDocument,
            UserJobBookmarkDocument,
            CoverLetterDocument
        ],
    )

    # 종료 시 close를 위해 client도 함께 반환
    return db, client
