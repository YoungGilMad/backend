# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.database import Base  # (이건 main.py 쪽에서 Base를 import 해오면 될 수도 있음)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)  # echo=True -> SQL 로그 출력

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)