# Priority 2: 단기 개선 (Short-term) 🔧

> **목표**: 성능 최적화 및 코드 품질 향상
> **기간**: 1주
> **영향도**: High

---

## Task 2.1: N+1 쿼리 문제 해결 🚀

**파일**: `app/core/routers/space.py:88`

**현재 문제**:
```python
# 링크마다 개별 쿼리 실행 (N+1 문제)
for link in scene["links"]:
    target_link = await db_manager.get_collection("links").find_one({'_id':link})
    target_name = await db_manager.get_scene(target_link['target_id'])
```

**개선 전략**:
```python
# MongoDB Aggregation Pipeline 사용
pipeline = [
    {"$match": {"_id": ObjectId(scene_id)}},
    {"$lookup": {
        "from": "links",
        "localField": "links",
        "foreignField": "_id",
        "as": "link_details"
    }},
    {"$lookup": {
        "from": "scenes",
        "localField": "link_details.target_id",
        "foreignField": "_id",
        "as": "target_scenes"
    }}
]
scene_with_links = await db.scenes.aggregate(pipeline).to_list(1)
```

**체크리스트**:
- [ ] `database.py`에 `get_scene_with_links()` 메서드 추가
- [ ] Aggregation pipeline 구현
- [ ] `space.py:88` 리팩토링
- [ ] `space.py:113-120` 씬 편집 페이지도 동일 적용
- [ ] 성능 측정 (Before/After)
- [ ] 대량 링크 시나리오 테스트 (10+ links)

**예상 효과**:
- 10개 링크: 11 queries → 1 query
- 응답 시간: 500ms → 50ms (10배 개선)

---

## Task 2.2: Form 클래스 리팩토링 🎨

**파일**: `app/core/schemas/space_model.py`

**현재 문제**:
- `CreateSceneForm`과 `UpdateSceneForm` 중복 코드 (~90%)
- 44-88줄과 90-132줄이 거의 동일

**개선 전략**:
```python
class BaseSceneForm:
    """공통 로직 추상화"""
    def __init__(self, request: Request):
        self.request = request
        self.errors = []
        self.form_data = {}

    async def load_data(self):
        """공통 데이터 로딩 로직"""
        form = await self.request.form()
        # ... 공통 로직

    def _process_multi_fields(self):
        """scene, x, y, z 등 멀티 필드 처리"""
        for field in ['scene', 'x', 'y', 'z', 'yaw', 'pitch', 'roll']:
            if hasattr(self, field) and len(getattr(self, field)) > 1:
                setattr(self, field, getattr(self, field)[1:])

class CreateSceneForm(BaseSceneForm):
    async def is_valid(self):
        # 파일 업로드 필수
        if not hasattr(self, 'file'):
            self.errors.append("Image File is required")
        return super().is_valid()

class UpdateSceneForm(BaseSceneForm):
    async def is_valid(self):
        # 파일 업로드 선택
        return super().is_valid()
```

**체크리스트**:
- [ ] `BaseSceneForm` 부모 클래스 생성
- [ ] 공통 로직 추출 (`load_data`, `_process_multi_fields`)
- [ ] `CreateSceneForm` 상속 구조로 변경
- [ ] `UpdateSceneForm` 상속 구조로 변경
- [ ] 기존 동작 회귀 테스트
- [ ] `UserRegisterForm`, `UserLoginForm`도 동일 패턴 적용 고려

**코드 감소**:
- 132 LOC → 80 LOC (40% 감소)

---

## Task 2.3: 환경 변수 관리 개선 🔐

**파일**: `app/core/instance/config.py` (Git에 미포함)

**현재 문제**:
- 설정 파일이 `.gitignore`되어 있어 협업 어려움
- 민감 정보와 일반 설정이 혼재

**개선 전략**:
```python
# .env 파일 사용
MONGODB_URL=mongodb://localhost:27017/
JWT_SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

**체크리스트**:
- [ ] `requirements.txt`에 `pydantic-settings` 추가
- [ ] `.env.example` 템플릿 파일 생성
- [ ] `app/core/config.py` 생성 (Pydantic Settings)
- [ ] `instance/config.py` → `.env` 마이그레이션
- [ ] 모든 import 경로 변경 (`from app.core import config`)
- [ ] `.gitignore`에 `.env` 추가
- [ ] README 설정 가이드 업데이트
- [ ] Docker Compose 환경 변수 통합

---

## Task 2.4: 로깅 시스템 추가 📝

**파일**: 신규 `app/core/libs/logger.py`

**현재 문제**:
- print 문으로 디버깅 (`database.py:97`, `space.py:219`)
- 운영 환경에서 추적 불가능
- 에러 발생 시 컨텍스트 부족

**개선 전략**:
```python
# logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("simulverse")
    logger.setLevel(logging.INFO)

    # 파일 핸들러 (5MB 로테이션)
    file_handler = RotatingFileHandler(
        "logs/simulverse.log",
        maxBytes=5*1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

# 사용 예
logger.info(f"User {user.email} created space {space_id}")
logger.error(f"Failed to update scene {scene_id}: {exc}")
```

**체크리스트**:
- [ ] `app/core/libs/logger.py` 생성
- [ ] `main.py`에 로거 초기화
- [ ] 주요 엔드포인트에 INFO 로그 추가
- [ ] 예외 핸들러에 ERROR 로그 추가
- [ ] DB 쿼리 실패 시 로깅
- [ ] `logs/` 디렉토리 생성 및 `.gitignore` 추가
- [ ] 주석 처리된 print 문 제거
- [ ] 로그 레벨별 필터링 테스트

**로그 구조**:
```
logs/
├── simulverse.log          # 현재 로그
├── simulverse.log.1        # 백업 1
└── simulverse.log.2        # 백업 2
```

---

## Task 2.5: 비동기 작업 최적화 ⚡

**파일**: `app/core/routers/space.py`, `app/core/models/database.py`

**현재 문제**:
```python
# 순차적 실행 (느림)
space = await db_manager.get_space(space_id)
scenes = await db_manager.get_scenes(space_id)
user = await db_manager.get_user(user_id)
```

**개선 전략**:
```python
import asyncio

# 병렬 실행
space, scenes, user = await asyncio.gather(
    db_manager.get_space(space_id),
    db_manager.get_scenes(space_id),
    db_manager.get_user(user_id)
)
```

**체크리스트**:
- [ ] `space.py:143-158` 뷰어 조회 병렬화
- [ ] `create.py` 공간 생성 시 유저 조회 병렬화
- [ ] `database.py:91-92` 업데이트 병렬화
- [ ] 성능 벤치마크 (Before/After)
- [ ] 타임아웃 설정 추가 (`asyncio.wait_for`)
- [ ] 에러 핸들링 개선 (부분 실패 처리)

**예상 효과**:
- 3개 독립 쿼리: 300ms → 100ms (3배 개선)

---

## Task 2.6: 테스트 환경 구축 🧪

**파일**: `tests/` 디렉토리 생성

**현재 문제**:
- 테스트 코드 부재
- 리팩토링 시 회귀 위험 높음

**개선 전략**:
```python
# tests/conftest.py
import pytest
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture
async def test_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["simulverse_test"]
    yield db
    await client.drop_database("simulverse_test")

# tests/test_auth.py
@pytest.mark.asyncio
async def test_create_user(test_db):
    form = UserRegisterForm(...)
    result = await db_manager.create_user(form)
    assert result == True
```

**체크리스트**:
- [ ] `tests/` 디렉토리 구조 생성
- [ ] `conftest.py` 픽스처 설정
- [ ] `test_auth.py` - 인증 테스트 (5개 케이스)
- [ ] `test_space.py` - 공간 관리 테스트 (8개 케이스)
- [ ] `test_database.py` - DB 레이어 테스트 (10개 케이스)
- [ ] pytest-asyncio 설정
- [ ] CI/CD 파이프라인 연동 준비
- [ ] 커버리지 측정 설정 (pytest-cov)

**목표 커버리지**: 60% 이상

---

## Task 2.7: API 응답 표준화 📦

**파일**: 신규 `app/core/schemas/response_model.py`

**현재 문제**:
- 일부는 HTML, 일부는 JSON 응답
- 에러 응답 형식 불일치

**개선 전략**:
```python
from pydantic import BaseModel

class APIResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None
    message: str = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int

# 사용
return APIResponse(
    success=True,
    data={"space_id": str(space_id)},
    message="Space created successfully"
)
```

**체크리스트**:
- [ ] `response_model.py` 생성
- [ ] API 엔드포인트 응답 형식 통일
- [ ] 페이지네이션 공통 모델 적용
- [ ] OpenAPI 스키마 문서화
- [ ] 프론트엔드에서 응답 파싱 로직 업데이트
- [ ] 에러 코드 체계 정립 (E001, E002, ...)

---

## 완료 기준 (Definition of Done)

✅ 모든 체크리스트 항목 완료
✅ N+1 쿼리 해결 (성능 5배 이상 개선)
✅ 단위 테스트 60% 커버리지 달성
✅ 로그 시스템 운영 가능
✅ 환경 변수 분리 완료
✅ 코드 리뷰 및 페어 프로그래밍 완료
✅ Git 커밋 및 태그 (`v0.3.0-performance`)

---

## 예상 소요 시간
- Task 2.1: 6시간 (N+1 해결)
- Task 2.2: 4시간 (Form 리팩토링)
- Task 2.3: 3시간 (환경 변수)
- Task 2.4: 3시간 (로깅)
- Task 2.5: 4시간 (비동기 최적화)
- Task 2.6: 8시간 (테스트 작성)
- Task 2.7: 4시간 (API 표준화)
- **총계**: 32시간 (약 4-5일)
