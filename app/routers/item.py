# app/routers/item.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

router = APIRouter(
    prefix="/item",
    tags=["Item"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/avatar-buy/{user_id}/{item_id}")
def buy_avatar(user_id: int, item_id: int, db: Session = Depends(get_db)):
    # 아이템 존재 확인
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.item_type != "avatar":
        raise HTTPException(status_code=400, detail="Not an avatar item")

    # 코인 차감 로직, 영수증 기록 등
    hero = db.query(models.Hero).filter(models.Hero.user_id == user_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    if hero.coin < item.price:
        raise HTTPException(status_code=400, detail="Insufficient coin")

    hero.coin -= item.price
    db.commit()

    # Receipt에 기록
    receipt = models.Receipt(user_id=user_id, item_id=item_id)
    db.add(receipt)
    db.commit()
    return {"message": "Avatar item purchased successfully."}

@router.post("/avatar-wear/{user_id}/{item_id}")
def wear_avatar(user_id: int, item_id: int, db: Session = Depends(get_db)):
    # hero.avatar_id = item_id 로 세팅
    hero = db.query(models.Hero).filter(models.Hero.user_id == user_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.item_type != "avatar":
        raise HTTPException(status_code=400, detail="Not an avatar item")

    hero.avatar_id = item_id
    db.commit()
    return {"message": f"Avatar changed to item {item_id}"}

# 배경 구매/착용, 아이템 삭제, 코인 업데이트 등 유사 로직으로 구현