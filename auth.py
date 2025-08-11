import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- 설정 ---
# 비밀 키, 알고리즘, 토큰 만료 시간 설정
# 이 SECRET_KEY는 절대 코드에 하드코딩하면 안 됩니다! (환경 변수 사용 권장)
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 스킴 정의
# tokenUrl은 토큰을 발급해주는 엔드포인트의 주소를 가리킴
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# --- 헬퍼 함수 ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """일반 비밀번호와 해싱된 비밀번호가 일치하는지 확인"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호를 해싱"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # JWT 생성: payload, secret_key, algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- 핵심 의존성 함수 ---

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    토큰을 검증하고 현재 사용자를 반환하는 의존성 함수.
    이 함수를 Depends()로 주입하면 엔드포인트가 보호됩니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 토큰 디코딩 및 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # 여기에 TokenData 같은 Pydantic 모델로 한번 더 검증할 수 있습니다.
    except JWTError:
        raise credentials_exception
    
    # 실제 애플리케이션에서는 DB에서 사용자 정보를 조회해야 합니다.
    # user = user_repository.get_by_username(db, username=username)
    # 이 예제에서는 간단히 페이로드 자체를 반환합니다.
    # if user is None:
    #     raise credentials_exception
    return {"username": username} # 실제로는 DB에서 조회한 User 객체를 반환