# my_backend

이 저장소는 FastAPI로 만든 예시 백엔드입니다.

## 1. 환경 설정

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env의 DATABASE_URL 경로로 접속 가능한 DB 생성
createdb mydatabase

uvicorn app.main:app --reload

---

## 4. app/\_\_init\_\_.py

보통은 비어있어도 됩니다.

```python
# app/__init__.py