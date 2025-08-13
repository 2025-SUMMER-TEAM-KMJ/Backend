from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """회원가입 요청 시 사용하는 모델"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=2)

class Token(BaseModel):
    """클라이언트에게 반환될 액세스 토큰 모델"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """토큰의 payload에 담길 데이터 모델"""
    username: str | None = None