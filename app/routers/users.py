from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.auth import authenticate_user, create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas
from ..utils import auth
from sqlalchemy.orm import Session 

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
    return await auth.create_user(db=db, user_data=user)

<<<<<<< HEAD
# 로그인
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 사용자 인증
    user = await auth.authenticate_user(db, login_data.email, login_data.password)
=======
# login: OAuth2 사용하도록 수정
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
>>>>>>> origin/dev
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
<<<<<<< HEAD
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
=======
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
>>>>>>> origin/dev

# 현재 사용자 정보 조회
@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
<<<<<<< HEAD
    return UserResponse.model_validate(current_user)
=======
    return current_user

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from ..utils.file_handler import save_upload_file
import os

# 이미지 저장 경로 설정
UPLOAD_DIR = "uploads/profile_images"

@router.post("/me/profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 파일 형식 검증
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        # 이전 프로필 이미지가 있다면 삭제
        if current_user.profile_img and os.path.exists(current_user.profile_img):
            os.remove(current_user.profile_img)
        
        # 새 이미지 저장
        file_path = await save_upload_file(file, UPLOAD_DIR)
        
        # DB 업데이트
        current_user.profile_img = file_path
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        
        return {"message": "Profile image updated successfully", "file_path": file_path}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# 프로필 이미지 조회 엔드포인트
@router.get("/me/profile-image")
async def get_profile_image(
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.profile_img:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile image not found"
        )
    
    return {"profile_img": current_user.profile_img}

# user 이름 조회 엔드포인트
@router.get("/me/user-name")
async def get_user_name(
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    현재 로그인된 사용자의 이름을 가져옵니다.
    """
    if not current_user.name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User name not found"
        )
    
    print(current_user.name)
    
    return {"name": current_user.name}

@router.post("/me/user-name")
async def update_user_name(
    name: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 로그인된 사용자의 이름을 업데이트합니다.
    """
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )
    
    current_user.name = name
    db.add(current_user)  # 변경사항을 스테이징
    await db.commit()          # 변경사항을 커밋
    await db.refresh(current_user)  # DB에서 최신 데이터로 리프레시

    print(current_user.name)
    
    return {"name": current_user.name}
>>>>>>> origin/dev
