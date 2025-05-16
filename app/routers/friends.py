from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel  # ✅ 추가!
from app.database import get_db
from app import models
from app.models import User, Friend

router = APIRouter(
    prefix="/friends",
    tags=["friends"]
)

# 친구 목록 조회
@router.get("/{user_id}")
async def get_friends(user_id: int, db: AsyncSession = Depends(get_db)):
    # 유저 존재 여부 확인
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 친구 목록 가져오기
    result = await db.execute(
        select(User)
        .join(Friend, Friend.friend_user_id == User.id)
        .filter(Friend.user_id == user_id)
    )
    friends = result.scalars().all()

    return [
        {
            "id": f.id,
            "name": f.name,
            "level": f.level,
            "profile_img": f.profile_img,
            "ranking": f.ranking,
            "xp": f.xp,
            "strength": f.strength,
            "agility": f.agility,
            "intelligence": f.intelligence,
            "stamina": f.stamina,
        }
        for f in friends
    ]

# 친구 추가
class FriendAddRequest(BaseModel):
    user_id: int
    friend_user_id: int

@router.post("/add")
async def add_friend(request: FriendAddRequest, db: AsyncSession = Depends(get_db)):
    new_friend = models.Friend(
        user_id=request.user_id,
        friend_user_id=request.friend_user_id
    )
    db.add(new_friend)
    await db.commit()
    return {"message": "Friend added"}
