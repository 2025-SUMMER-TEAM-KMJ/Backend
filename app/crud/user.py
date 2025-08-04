# app/crud/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_pw = hash_password(user_in.password)

    user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        name=user_in.name,
        age=user_in.age,
        gender=user_in.gender,
        phone=user_in.phone
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
