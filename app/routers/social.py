# app/routers/social.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

router = APIRouter(
    prefix="/social",
    tags=["Social"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/friend/add/{user_id}/{friend_id}")
def add_friend(user_id: int, friend_id: int, db: Session = Depends(get_db)):
    # 친구 중복 체크
    existing = db.query(models.Friend).filter(
        models.Friend.user_id == user_id,
        models.Friend.friend_user_id == friend_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already friends")
    new_friend = models.Friend(user_id=user_id, friend_user_id=friend_id)
    db.add(new_friend)
    db.commit()
    return {"message": f"User {friend_id} added as friend."}

@router.delete("/friend/remove/{user_id}/{friend_id}")
def remove_friend(user_id: int, friend_id: int, db: Session = Depends(get_db)):
    friendship = db.query(models.Friend).filter(
        models.Friend.user_id == user_id,
        models.Friend.friend_user_id == friend_id
    ).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
    db.delete(friendship)
    db.commit()
    return {"message": f"Removed friend {friend_id}"}

@router.get("/friend/wake-up/{user_id}/{target_id}")
def wake_up_friend(user_id: int, target_id: int):
    # 예: target_id 유저에게 "user_id가 깨웠다" 알림. 푸시 서버 연동 등
    return {"message": f"User {target_id} has been woken up by {user_id}!"}

@router.post("/group/make/{user_id}")
def make_group(user_id: int, name: str, description: str, db: Session = Depends(get_db)):
    new_group = models.Group(name=name, description=description, owner_id=user_id)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return {"message": "Group created", "group_id": new_group.id}

@router.post("/group/invite/{user_id}/{group_id}")
def invite_to_group(user_id: int, group_id: int, db: Session = Depends(get_db)):
    # 그룹 초대 로직 (알림 or group_members 추가 등)
    new_member = models.GroupMember(group_id=group_id, user_id=user_id)
    db.add(new_member)
    db.commit()
    return {"message": f"User {user_id} invited to group {group_id}"}

@router.post("/group/join/{user_id}/{group_id}")
def join_group(user_id: int, group_id: int, db: Session = Depends(get_db)):
    # 가입
    new_member = models.GroupMember(group_id=group_id, user_id=user_id)
    db.add(new_member)
    db.commit()
    return {"message": f"User {user_id} joined group {group_id}"}

@router.delete("/group/leave/{user_id}/{group_id}")
def leave_group(user_id: int, group_id: int, db: Session = Depends(get_db)):
    member = db.query(models.GroupMember).filter(
        models.GroupMember.group_id == group_id,
        models.GroupMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Not in group")
    db.delete(member)
    db.commit()
    return {"message": f"User {user_id} left group {group_id}"}

@router.delete("/group/remove/{group_id}")
def remove_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()
    return {"message": f"Group {group_id} deleted"}