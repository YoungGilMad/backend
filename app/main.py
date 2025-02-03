# app/main.py

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users, hero, item, quest, social, settings
from fastapi.middleware.cors import CORSMiddleware
from app import models
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="My MiniHome Backend",
    description="Flutter 연동용 백엔드 API",
    version="1.0.0"
)

# 비동기 데이터베이스 초기화
async def init_db():
    print(22)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 애플리케이션 시작 시 DB 초기화
@app.on_event("startup")
async def startup_event():
    await init_db()

# CORS (Flutter 등에서 접근 시 필요할 수 있음)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 도메인을 구체적으로 넣는 것이 안전
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users.router)
app.include_router(hero.router)
app.include_router(item.router)
app.include_router(quest.router)
app.include_router(social.router)
app.include_router(settings.router)

# 헬스 체크 용도
@app.get("/")
def root():
    return {"message": "Hello, FastAPI World!"}

# 디렉토리 생성 (프로필 처리용)
os.makedirs("uploads/profile_images", exist_ok=True)

# mount
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

