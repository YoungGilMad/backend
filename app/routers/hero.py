# app/routers/hero.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas

router = APIRouter(
    prefix="/hero",
    tags=["Hero"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/make/{user_id}")
def create_hero(user_id: int, db: Session = Depends(get_db)):
    # 이미 해당 user_id에 hero가 있는지 확인 (1:1 관계)
    hero = db.query(models.Hero).filter(models.Hero.user_id == user_id).first()
    if hero:
        raise HTTPException(status_code=400, detail="Hero already exists for this user")

    new_hero = models.Hero(
        user_id=user_id,
        hero_level=1,
        coin=0,
        avatar_id=0,
        background_id=0
    )
    db.add(new_hero)
    db.commit()
    db.refresh(new_hero)
    return {"message": f"Hero created for user {user_id}"}

@router.put("/edit/{user_id}")
def edit_hero(user_id: int, hero_data: schemas.HeroBase, db: Session = Depends(get_db)):
    hero = db.query(models.Hero).filter(models.Hero.user_id == user_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found for this user")

    hero.hero_level = hero_data.hero_level
    hero.coin = hero_data.coin
    hero.avatar_id = hero_data.avatar_id
    hero.background_id = hero_data.background_id
    db.commit()
    db.refresh(hero)
    return {"message": "Hero updated", "hero": hero_data}

@router.post("/level-up/{user_id}")
def level_up_hero(user_id: int, db: Session = Depends(get_db)):
    hero = db.query(models.Hero).filter(models.Hero.user_id == user_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero.hero_level += 1
    db.commit()
    db.refresh(hero)
    return {"message": f"Hero level up! Current level: {hero.hero_level}"}

@router.post("/reward/{user_id}")
def reward_hero(user_id: int, reward_coin: int = 10, db: Session = Depends(get_db)):
    # 예시: 퀘스트 완료 보상
    hero = db.query(models.Hero).filter(models.Hero.user_id == user_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero.coin += reward_coin
    db.commit()
    db.refresh(hero)
    return {"message": f"Reward given. Current coin: {hero.coin}"}