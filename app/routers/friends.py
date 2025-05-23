from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.database import get_db
from app import models
from app.models import User, Friend

router = APIRouter(
    prefix="/friends",
    tags=["friends"]
)

# ===============================
# ✅ 친구 목록 조회
# ===============================
@router.get("/{user_id}")
async def get_friends(user_id: int, db: AsyncSession = Depends(get_db)):
    # 유저 존재 여부 확인
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 친구 목록 조회: Hero가 없는 친구도 포함
    stmt = (
        select(models.User, models.Hero)
        .join(models.Friend, models.Friend.friend_user_id == models.User.id)
        .outerjoin(models.Hero, models.Hero.user_id == models.User.id)
        .filter(models.Friend.user_id == user_id)
    )
    result = await db.execute(stmt)
    rows = result.all()  # [(User, Hero or None)]

    return [
        {
            "id": str(u.id),
            "name": u.name,
            "level": h.hero_level if h else 1,
            "profile_img": u.profile_img,
            "ranking": h.coin if h else 0,
            "xp": 0,
            "strength": h.strength if h else 0,
            "agility": h.skill if h else 0,  # agility = skill
            "intelligence": h.intelligence if h else 0,
            "stamina": h.stamina if h else 0,
        }
        for u, h in rows
    ]

# ===============================
# ✅ 친구 추가
# ===============================
class FriendAddRequest(BaseModel):
    user_id: int
    friend_user_id: int

@router.post("/add")
async def add_friend(request: FriendAddRequest, db: AsyncSession = Depends(get_db)):
    user_id = request.user_id
    friend_user_id = request.friend_user_id

    # 양방향 친구 관계 추가
    friend1 = models.Friend(user_id=user_id, friend_user_id=friend_user_id)
    friend2 = models.Friend(user_id=friend_user_id, friend_user_id=user_id)
    db.add_all([friend1, friend2])

    try:
        await db.commit()
    except:
        await db.rollback()
        raise HTTPException(status_code=400, detail="이미 친구로 등록되어 있습니다.")

    return {"message": "친구가 추가되었습니다."}
