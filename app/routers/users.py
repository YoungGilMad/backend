from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas
from ..utils import auth

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# 회원가입 요청 모델
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone_number: Optional[str] = None
    
    class Config:
        from_attributes = True

# 로그인 요청 모델
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True

# 사용자 응답 모델
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone_number: Optional[str]
    profile_img: Optional[str]
    join_date: datetime
    update_date: datetime

    class Config:
        from_attributes = True

# 로그인 응답 모델
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

    class Config:
        from_attributes = True

# 회원가입
@router.post("/register", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await auth.create_user(db=db, user=user)

# 로그인
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 사용자 인증
    user = await auth.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 생성
    access_token = auth.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # UserResponse 모델로 변환하여 반환
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone_number=user.phone_number,
        profile_img=user.profile_img,
        join_date=user.join_date,
        update_date=user.update_date
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# 현재 사용자 정보 조회
@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return UserResponse.model_validate(current_user)