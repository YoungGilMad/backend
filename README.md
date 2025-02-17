# beHero Backend

FastAPI 기반의 영웅 육성 소셜 게임 백엔드 서버

## 기술 스택

- Python 3.8+
- FastAPI
- SQLAlchemy (ORM)
- JWT 인증
- async/await 지원

## 주요 기능

- 사용자 인증 (JWT)
- 영웅 캐릭터 관리
- 퀘스트 시스템
- 아이템 상점
- 소셜 기능 (친구, 그룹)
- 설정 관리

## 시작하기

### 필수 조건

- Python 3.8 이상
- pip (Python 패키지 관리자)
- 가상환경 (권장)

### 설치

1. 저장소 클론
```bash
git clone [repository-url]
cd beHero
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성하고 다음 내용을 추가:
```
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 실행

개발 서버 실행:
```bash
uvicorn app.main:app --reload
```

서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

### API 문서

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 프로젝트 구조

```
beHero/
├── app/
│   ├── routers/         # API 엔드포인트
│   ├── models/          # 데이터베이스 모델
│   ├── schemas/         # Pydantic 모델
│   ├── core/           # 핵심 기능 (인증 등)
│   └── utils/          # 유틸리티 함수
├── tests/              # 테스트 코드 (추가 예정)
└── requirements.txt    # 의존성 목록
```

## API 엔드포인트

주요 API 그룹:
- `/users` - 사용자 관리
- `/hero` - 영웅 캐릭터 관리
- `/quest` - 퀘스트 시스템
- `/item` - 아이템 관리
- `/social` - 소셜 기능
- `/settings` - 설정 관리

자세한 API 문서는 서버 실행 후 Swagger UI에서 확인할 수 있습니다.

## 개발 가이드

### 코드 스타일
- PEP 8 준수
- Black 포맷터 사용 권장
- isort로 import 정렬

### 브랜치 전략
- main: 프로덕션 환경
- develop: 개발 환경
- feature/*: 새로운 기능 개발
- bugfix/*: 버그 수정

### 커밋 메시지 컨벤션
```
feat: 새로운 기능
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 코드
chore: 기타 변경사항
develop: 개발 사항
```

## 라이센스

[라이센스 정보 추가]

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
