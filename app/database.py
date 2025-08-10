# app/database.py
import os
from typing import Callable
from pymongo import MongoClient
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# 현재는 로컬용으로 사용 -> 추후 수정 예정
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "app_db")

# Mongo 클라이언트/DB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# FastAPI DI: 특정 컬렉션 주입
def get_collection(name: str) -> Callable[[], object]:
    def _dep():
        return db[name]
    return _dep

# 앱 시작 시 1회: 인덱스 초기화
def init_indexes() -> None:
    db["users"].create_index("email", unique=True)
    db["refresh_tokens"].create_index([("user_id", 1), ("token", 1)], unique=True)
    db["refresh_tokens"].create_index("expires_at", expireAfterSeconds=0)

    # 자연어 검색용 text index (필요 필드 계속 추가 가능)
    db["wanted_job_postings"].create_index(
        [
            ("detail.intro", "text"),
            ("detail.main_tasks", "text"),
            ("detail.requirements", "text"),
            ("detail.preferred_points", "text"),
            ("company.name", "text"),
            ("detail.position.job", "text"),
            ("detail.position.jobGroup", "text"),
        ],
        name="job_text_index",
        default_language="korean",
    )
    db["wanted_job_postings"].create_index("status")
    db["wanted_job_postings"].create_index("due_time")
