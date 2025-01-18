# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app import models, schemas
from app.core.utils import hash_password, verify_password
from app.core.security import create_access_token


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    existing_user = db.query(models.User).filter(models.User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    # 비밀번호 해싱
    hashed_pw = hash_password(user_create.password)

    new_user = models.User(
        name=user_create.name,
        phone_number=user_create.phone_number,
        email=user_create.email,
        password=hashed_pw,
        profile_img=user_create.profile_img
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=TokenResponse)  # 혹은 Dict
def login(request_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request_data.email).first()
    ...
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # 비밀번호 검증
    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # JWT 토큰 발급
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/remove/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} removed."}

@router.get("/alarm/{user_id}")
def get_alarm(user_id: int):
    # 예시: 알림 기능 (DB에 알림 테이블이 있다면, 해당 데이터를 조회하는 형태)
    return {"user_id": user_id, "alarms": ["퀘스트 완료 알림", "친구가 나를 깨웠음"]}