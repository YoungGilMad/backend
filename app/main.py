# app/main.py

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users, hero, item, quest, social, settings
from fastapi.middleware.cors import CORSMiddleware

# DB 초기화 (테이블 생성)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My MiniHome Backend",
    description="Flutter 연동용 백엔드 API",
    version="1.0.0"
)

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