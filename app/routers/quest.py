from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.database import get_db
from app import models
from sqlalchemy.future import select
from app.database import SessionLocal
from pydantic import BaseModel

router = APIRouter(
    prefix="/quest",
    tags=["Quest"]
)

class QuestCreateRequest(BaseModel):
    title: str
    description: str
    
    
async def get_db():
    async with SessionLocal() as db:
        yield db

# ✅ 퀘스트 조회
@router.get("/info/{quest_id}")
async def get_quest_info(quest_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Quest).filter(models.Quest.id == quest_id))
    quest = result.scalars().first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest

# ✅ 자기주도 퀘스트 생성
@router.post("/self-gen/{user_id}")
async def create_self_quest(user_id: int, request: QuestCreateRequest, db: AsyncSession = Depends(get_db)):
    new_quest = models.Quest(
        user_id=user_id,
        title=request.title,
        description=request.description,
        quest_type="self"
    )
    db.add(new_quest)
    await db.commit()
    await db.refresh(new_quest)
    return {"message": "Self quest created", "quest": new_quest}

# ✅ 자기주도 퀘스트 클리어
@router.put("/self-clear/{quest_id}")
async def clear_self_quest(quest_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Quest).filter(models.Quest.id == quest_id))
    quest = result.scalars().first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    quest.finish = True
    quest.finish_time = func.now()
    await db.commit()
    return {"message": f"Quest {quest_id} completed"}

# ✅ 히어로 퀘스트 생성
@router.post("/ai-gen/{user_id}")
async def create_ai_quest(user_id: int, db: AsyncSession = Depends(get_db)):
    new_quest = models.Quest(
        user_id=user_id,
        description="AI가 생성한 퀘스트 내용",
        quest_type="ai"
    )
    db.add(new_quest)
    await db.commit()
    await db.refresh(new_quest)
    return {"message": "AI quest created", "quest_id": new_quest.id}

# ✅ 히어로 퀘스트 클리어
@router.put("/ai-clear/{quest_id}")
async def clear_ai_quest(quest_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Quest).filter(models.Quest.id == quest_id))
    quest = result.scalars().first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    quest.finish = True
    quest.finish_time = func.now()
    await db.commit()
    return {"message": f"AI quest {quest_id} completed"}

# ✅ 퀘스트 삭제
@router.delete("/remove/{quest_id}")
async def remove_quest(quest_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Quest).filter(models.Quest.id == quest_id))
    quest = result.scalars().first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    await db.delete(quest)
    await db.commit()
    return {"message": f"Quest {quest_id} removed"}

# ✅ 유저의 전체 퀘스트 목록 조회
@router.get("/list/{user_id}")
async def get_user_quests(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Quest).filter(models.Quest.user_id == user_id))
    quests = result.scalars().all()
    return quests