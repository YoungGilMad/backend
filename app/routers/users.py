from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas
from ..utils import auth
from sqlalchemy import select
from sqlalchemy import insert  # 상단에 추가

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
    hero_level: Optional[int] = 1  # Optional로 변경

    class Config:
        from_attributes = True
        orm_mode = True

# 로그인 응답 모델
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

    class Config:
        from_attributes = True

# 회원가입
@router.post("/register", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 이메일 중복 체크
    db_user = await auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 사용자 생성
    new_user = await auth.create_user(db=db, user=user)

    # ✅ Hero 자동 생성
    await db.execute(
        insert(models.Hero).values(
            user_id=new_user.id,
            hero_level=1,
            coin=0,
            avatar_id=0,
            background_id=0
        )
    )
    await db.commit()
    
    # 응답 데이터 구성
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        phone_number=new_user.phone_number,
        profile_img=new_user.profile_img,
        join_date=new_user.join_date,
        update_date=new_user.update_date,
        hero_level=1
    )


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
    
    # 사용자의 hero 정보 조회
    result = await db.execute(
        select(models.Hero).filter(models.Hero.user_id == user.id)
    )
    hero = result.scalar_one_or_none()
    
    # 응답 데이터 구성
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone_number=user.phone_number,
        profile_img=user.profile_img,
        join_date=user.join_date,
        update_date=user.update_date,
        hero_level=hero.hero_level if hero else 1
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

# 모든 유저 반환
@router.get("/all", response_model=list[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return [UserResponse.from_orm(user) for user in users]

# 전체 사용자 랭킹 조회 (hero_level 기준 내림차순, 이름 기준 오름차순)
@router.get("/ranking")
async def get_user_ranking(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User, models.Hero)
        .join(models.Hero, models.User.id == models.Hero.user_id)
        .order_by(models.Hero.hero_level.desc(), models.User.name.asc())
    )
    rows = result.all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "profile_img": user.profile_img,
            "hero_level": hero.hero_level
        }
        for user, hero in rows
    ]