from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine
from .config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
    future=True
)

# 비동기 세션
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 동기 세션 - 기존 코드와의 호환성을 위해 추가
SessionLocal = AsyncSessionLocal

Base = declarative_base()

# DB 세션 의존성
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()