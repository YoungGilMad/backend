from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.auth import authenticate_user, create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
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
    nickname: str
    
    class Config:
        from_attributes = True

# 로그인 요청 모델
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True

# 회원가입
@router.post("/", response_model=schemas.User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await auth.create_user(db=db, user_data=user)

# login: OAuth2 사용하도록 수정
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# 현재 사용자 정보 조회
@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
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