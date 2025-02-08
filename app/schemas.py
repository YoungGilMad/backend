from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(BaseModel):
    email: str
    password: str
    phone_number: Optional[str] = None
    nickname: str

class User(UserBase):
    id: int
    phone_number: Optional[str] = None
    profile_img: Optional[str] = None
    join_date: datetime
    update_date: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 모델과의 호환성을 위해 필요

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

    class Config:
        from_attributes = True

class HeroBase(BaseModel):
    hero_level: int = 1
    coin: int = 0
    avatar_id: Optional[int] = None
    background_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class HeroCreate(HeroBase):
    user_id: int

class HeroUpdate(HeroBase):
    pass

class Hero(HeroBase):
    id: int
    user_id: int
    tag: Optional[List[str]] = None
    did_info: Optional[List[dict]] = None
    
    class Config:
        from_attributes = True