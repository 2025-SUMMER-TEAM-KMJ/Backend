# app/core/security.py
import os
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from settings import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Password Hashing

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(sub: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "typ": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token() -> str:
    # DB에 저장할 랜덤 문자열
    return secrets.token_urlsafe(64)

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
