# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 1) User
class UserBase(BaseModel):
    name: str
    phone_number: Optional[str] = None
    email: EmailStr
    profile_img: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    join_date: datetime
    update_date: datetime

    class Config:
        orm_mode = True

# 2) Hero
class HeroBase(BaseModel):
    hero_level: int
    coin: int
    avatar_id: Optional[int] = None
    background_id: Optional[int] = None

class HeroCreate(HeroBase):
    pass

class HeroResponse(HeroBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# 3) 기타 필요한 스키마들 (Item, Quest 등)도 예시