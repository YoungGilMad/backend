# app/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timedelta

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255))
    profile_img = Column(String)
    join_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # hero = relationship("Hero", back_populates="user", uselist=False)
    # quests = relationship("Quest", back_populates="user")

class Hero(Base):
    __tablename__ = "heroes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    hero_level = Column(Integer, default=1)
    coin = Column(Integer, default=0)
    avatar_id = Column(Integer)
    background_id = Column(Integer)
    # 태그나 did_info를 문자열(JSON)로 저장하거나, PostgreSQL이라면 배열 타입을 쓸 수도 있음.

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    contents = Column(String)
    img = Column(String)  # url
    create_at = Column(DateTime, server_default=func.now())

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    item_type = Column(String(50))  # enum 대체 (avatar, background, etc)

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))

class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String(200))
    tag = Column(String)  # JSON이나 CSV 등으로 저장하려면 별도 처리
    days = Column(String) # 마찬가지로 JSON 배열로 저장한다면 Column(JSON) 고려
    finish = Column(Boolean, default=False)
    quest_type = Column(String(50))  # 'ai', 'self', etc.
    start_time = Column(DateTime)
    stop_time = Column(DateTime)
    finish_time = Column(DateTime)
    progress_time = Column(Integer)  # 필요하다면
    complete_time = Column(Integer)  # 필요하다면
    deadline = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))

class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    friend_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    joined_at = Column(DateTime, server_default=func.now())

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())