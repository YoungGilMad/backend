# app/routers/settings.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

router = APIRouter(
    prefix="/setting",
    tags=["Settings"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/profile/{user_id}")
def change_profile_image(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 파일 저장 로직 (예: S3, static 폴더에 저장 등)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 실제로는 파일을 특정 위치에 저장 후, 경로(URL)를 DB에 저장
    # 여기서는 단순 예시
    user.profile_img = f"uploaded/{file.filename}"
    db.commit()
    db.refresh(user)
    return {"message": "Profile updated", "profile_img": user.profile_img}