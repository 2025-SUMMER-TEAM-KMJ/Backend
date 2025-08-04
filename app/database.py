# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 일단 SQLite 기준으로 생성(추후 변경)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# DB 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False}
)

# 세션 객체
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스: models가 상속할 부모
Base = declarative_base()

# Dependency: 요청마다 DB 세션 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
