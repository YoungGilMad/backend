from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    nickname: str

class UserCreate(BaseModel):
    email: str
    password: str
    nickname: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Hero 관련 스키마 추가
class HeroBase(BaseModel):
    name: str
    level: int = 1
    exp: int = 0
    hp: int = 100
    mp: int = 100
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    wisdom: int = 10

    class Config:
        from_attributes = True

class HeroCreate(HeroBase):
    user_id: int

class Hero(HeroBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True