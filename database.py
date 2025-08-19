# app/database.py
import os
import motor.motor_asyncio
from beanie import init_beanie
from models.user_document import UserDocument
from models.refresh_token_document import RefreshTokenDocument
from models.job_posting_document import JobPostingDocument
from models.user_job_bookmark_document import UserJobBookmarkDocument
from models.cover_letter_document import CoverLetterDocument
from settings import MONGO_URI, DB_NAME
from bson.codec_options import CodecOptions, UuidRepresentation

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

    codec_opts = CodecOptions(uuid_representation=UuidRepresentation.STANDARD)
    db = client.get_database(DB_NAME, codec_options=codec_opts)

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
