# app/routers/quest.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

router = APIRouter(
    prefix="/quest",
    tags=["Quest"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/info/{quest_id}")
def get_quest_info(quest_id: int, db: Session = Depends(get_db)):
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest

@router.post("/self-gen/{user_id}")
def create_self_quest(user_id: int, todo: str, db: Session = Depends(get_db)):
    new_quest = models.Quest(
        user_id=user_id,
        todo=todo,
        quest_type="self"
    )
    db.add(new_quest)
    db.commit()
    db.refresh(new_quest)
    return {"message": "Self quest created", "quest_id": new_quest.id}

@router.post("/self-clear/{quest_id}")
def clear_self_quest(quest_id: int, db: Session = Depends(get_db)):
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    quest.finish = True
    quest.finish_time = func.now()
    db.commit()
    return {"message": f"Quest {quest_id} completed"}

@router.post("/ai-gen/{user_id}")
def create_ai_quest(user_id: int, db: Session = Depends(get_db)):
    # 실제로는 AI 로직(챗GPT 등)으로 자동 생성. 여기서는 예시
    new_quest = models.Quest(
        user_id=user_id,
        todo="AI가 생성한 퀘스트 내용",
        quest_type="ai"
    )
    db.add(new_quest)
    db.commit()
    db.refresh(new_quest)
    return {"message": "AI quest created", "quest_id": new_quest.id}

@router.post("/ai-clear/{quest_id}")
def clear_ai_quest(quest_id: int, db: Session = Depends(get_db)):
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    quest.finish = True
    quest.finish_time = func.now()
    db.commit()
    return {"message": f"AI quest {quest_id} completed"}

@router.delete("/remove/{quest_id}")
def remove_quest(quest_id: int, db: Session = Depends(get_db)):
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    db.delete(quest)
    db.commit()
    return {"message": f"Quest {quest_id} removed"}