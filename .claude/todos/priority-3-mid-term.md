# Priority 3: 중기 개선 (Mid-term) 🏗️

> **목표**: 아키텍처 재설계 및 확장성 강화
> **기간**: 2-3주
> **영향도**: Medium (장기적 High)

---

## Task 3.1: 의존성 주입 패턴 적용 💉

**파일**: 전체 아키텍처 리팩토링

**현재 문제**:
```python
# 라우터에서 직접 DB 초기화
db_manager.init_manager(config.MONGODB_URL, "simulverse")

# 전역 싱글톤 사용
from ..models.database import db_manager
```

**개선 전략**:
```python
# app/core/dependencies.py
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class DatabaseService:
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
        self.db = client["simulverse"]

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """DB 의존성 주입"""
    yield db_service.db

# 라우터에서 사용
@router.get("/space/view/{space_id}")
async def space(
    request: Request,
    space_id: str,
    auth_user = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    space = await SpaceRepository(db).get_by_id(space_id)
```

**체크리스트**:
- [ ] `app/core/dependencies.py` 생성
- [ ] `DatabaseService` 클래스 구현
- [ ] `get_db()` 의존성 함수 작성
- [ ] `main.py`에서 DB 초기화 로직 이동
- [ ] 모든 라우터에 `db: Depends(get_db)` 추가
- [ ] `db_manager` 클래스 메서드 → 인스턴스 메서드 변환
- [ ] 라우터별 의존성 주입 테스트
- [ ] 순환 참조 제거 확인
- [ ] 단위 테스트에서 Mock DB 사용 가능하도록 개선

**장점**:
- 테스트 용이성 향상 (Mock DB 주입)
- DB 연결 풀 관리 개선
- 멀티 테넌트 지원 가능

---

## Task 3.2: Service 계층 분리 🎯

**파일**: 신규 `app/core/services/` 디렉토리

**현재 문제**:
```python
# database.py에 비즈니스 로직 혼재
@classmethod
async def create_space(cls, creator: str, space:CreateSpaceForm):
    # 권한 설정, 뷰어 관리 등 복잡한 로직
```

**개선 전략**:
```
app/core/
├── models/          # 데이터 모델 (Pydantic)
├── repositories/    # DB 접근 계층 (CRUD)
├── services/        # 비즈니스 로직 계층
└── routers/         # API 엔드포인트
```

**구현 예시**:
```python
# app/core/repositories/space_repository.py
class SpaceRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["spaces"]

    async def create(self, space_data: dict) -> ObjectId:
        result = await self.collection.insert_one(space_data)
        return result.inserted_id

    async def get_by_id(self, space_id: ObjectId) -> Optional[dict]:
        return await self.collection.find_one({"_id": space_id})

# app/core/services/space_service.py
class SpaceService:
    def __init__(self, space_repo: SpaceRepository, user_repo: UserRepository):
        self.space_repo = space_repo
        self.user_repo = user_repo

    async def create_space(self, creator_email: str, form: CreateSpaceForm) -> ObjectId:
        # 비즈니스 로직
        creator = await self.user_repo.get_by_email(creator_email)
        viewers = await self._build_viewers(creator, form)

        space_data = {
            "name": form.space_name,
            "creator": creator.id,
            "viewers": viewers,
            "scenes": {}
        }
        return await self.space_repo.create(space_data)

# app/core/routers/space.py
@router.post("/space/create")
async def create_space(
    form: CreateSpaceForm,
    auth_user = Depends(get_current_user),
    space_service: SpaceService = Depends(get_space_service)
):
    space_id = await space_service.create_space(auth_user.email, form)
    return {"space_id": str(space_id)}
```

**체크리스트**:
- [ ] `app/core/repositories/` 디렉토리 생성
- [ ] `SpaceRepository` 구현 (CRUD 메서드)
- [ ] `UserRepository` 구현
- [ ] `SceneRepository` 구현
- [ ] `LinkRepository` 구현
- [ ] `app/core/services/` 디렉토리 생성
- [ ] `SpaceService` 구현 (비즈니스 로직)
- [ ] `SceneService` 구현
- [ ] `AuthService` 구현
- [ ] 라우터에서 Service 사용하도록 리팩토링
- [ ] `database.py` 레거시 코드 제거
- [ ] 트랜잭션 처리 추가 (MongoDB 4.0+)
- [ ] 단위 테스트 작성 (각 계층별)

**코드 구조**:
```
services/
├── __init__.py
├── space_service.py      # 공간 관리 로직
├── scene_service.py      # 씬 관리 로직
├── auth_service.py       # 인증/권한 로직
└── user_service.py       # 사용자 관리 로직

repositories/
├── __init__.py
├── base_repository.py    # 공통 CRUD 메서드
├── space_repository.py
├── scene_repository.py
├── user_repository.py
└── link_repository.py
```

---

## Task 3.3: API 버전 관리 시스템 🔢

**파일**: `app/main.py`, `app/api/v1/`, `app/api/v2/`

**현재 문제**:
- API 변경 시 하위 호환성 깨짐
- 버전 없이 엔드포인트 노출

**개선 전략**:
```python
# app/api/v1/routers/space.py
router = APIRouter(prefix="/v1")

# app/api/v2/routers/space.py (새로운 응답 형식)
router = APIRouter(prefix="/v2")

# main.py
app.include_router(v1_router, prefix="/api")
app.include_router(v2_router, prefix="/api")

# 접근 경로
# /api/v1/space/view/{space_id}  (기존)
# /api/v2/spaces/{space_id}      (신규, RESTful)
```

**체크리스트**:
- [ ] `app/api/` 디렉토리 생성
- [ ] `app/api/v1/` 구조 생성 (기존 코드 이동)
- [ ] `app/api/v2/` 구조 생성 (개선된 API)
- [ ] v1 엔드포인트 deprecated 표시
- [ ] v2 RESTful 네이밍 규칙 적용
- [ ] API 버전별 스키마 분리
- [ ] OpenAPI 문서에 버전 표시
- [ ] 클라이언트 마이그레이션 가이드 작성
- [ ] v1 → v2 자동 리다이렉션 옵션 추가

**API v2 개선 사항**:
```
v1: POST /space/insert/{space_id}
v2: POST /api/v2/spaces/{space_id}/scenes

v1: GET /space/view/{space_id}
v2: GET /api/v2/spaces/{space_id}

v1: POST /space/delete/scene/{space_id}/{scene_id}
v2: DELETE /api/v2/spaces/{space_id}/scenes/{scene_id}
```

---

## Task 3.4: 캐싱 레이어 추가 ⚡

**파일**: 신규 `app/core/cache/redis_cache.py`

**현재 문제**:
- 동일 공간 조회 시 매번 DB 쿼리
- GridFS 이미지 다운로드 반복

**개선 전략**:
```python
# requirements.txt에 추가
redis>=5.0.0
aioredis>=2.0.0

# app/core/cache/redis_cache.py
from redis.asyncio import Redis
import json

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str):
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: any, ttl: int = 3600):
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

# 사용 예
@router.get("/space/view/{space_id}")
async def space(
    space_id: str,
    cache: CacheService = Depends(get_cache)
):
    # 캐시 확인
    cached = await cache.get(f"space:{space_id}")
    if cached:
        return cached

    # DB 조회
    space = await db_manager.get_space(space_id)

    # 캐시 저장 (1시간)
    await cache.set(f"space:{space_id}", space, ttl=3600)
    return space
```

**체크리스트**:
- [ ] Redis 설치 및 Docker Compose 추가
- [ ] `app/core/cache/redis_cache.py` 구현
- [ ] 캐시 의존성 함수 작성
- [ ] 공간 조회 API에 캐싱 적용
- [ ] 사용자 정보 캐싱
- [ ] 씬 리스트 캐싱
- [ ] GridFS 이미지 캐싱 (CDN 대안)
- [ ] 캐시 무효화 로직 (업데이트/삭제 시)
- [ ] 캐시 히트율 모니터링
- [ ] TTL 전략 수립 (공간: 1시간, 사용자: 30분)

**예상 효과**:
- 공간 조회 응답: 100ms → 5ms (20배)
- DB 부하: 50% 감소
- 동시 접속자 처리: 2배 향상

---

## Task 3.5: 이벤트 기반 아키텍처 도입 📡

**파일**: 신규 `app/core/events/` 디렉토리

**현재 문제**:
```python
# 공간 생성 시 다양한 작업이 결합됨
await create_space()
await update_user_spaces()
await send_notification()  # 미래에 추가 시 복잡도 증가
await log_activity()
```

**개선 전략**:
```python
# app/core/events/event_bus.py
from typing import Callable, List
from dataclasses import dataclass

@dataclass
class Event:
    type: str
    data: dict

class EventBus:
    def __init__(self):
        self._handlers: dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: Event):
        handlers = self._handlers.get(event.type, [])
        await asyncio.gather(*[h(event.data) for h in handlers])

# app/core/events/handlers.py
async def on_space_created(data: dict):
    """공간 생성 이벤트 핸들러"""
    logger.info(f"Space created: {data['space_id']}")
    # 알림, 로깅 등

async def on_user_invited(data: dict):
    """사용자 초대 이벤트 핸들러"""
    # 이메일 발송 (미래)
    pass

# 사용
@router.post("/space/create")
async def create_space(
    form: CreateSpaceForm,
    event_bus: EventBus = Depends(get_event_bus)
):
    space_id = await space_service.create_space(form)

    # 이벤트 발행
    await event_bus.publish(Event(
        type="space.created",
        data={"space_id": space_id, "creator": auth_user.email}
    ))

    return {"space_id": space_id}
```

**체크리스트**:
- [ ] `app/core/events/event_bus.py` 구현
- [ ] 이벤트 타입 정의 (`space.created`, `scene.updated`, etc.)
- [ ] 핸들러 등록 시스템 구현
- [ ] 공간 생성 이벤트 적용
- [ ] 씬 업데이트 이벤트 적용
- [ ] 사용자 초대 이벤트 적용
- [ ] 이벤트 로깅 핸들러 작성
- [ ] 비동기 처리 실패 시 재시도 로직
- [ ] 이벤트 소싱 준비 (선택사항)

**미래 확장**:
- 이메일 알림 시스템
- 웹훅 통합
- 실시간 협업 알림
- 활동 로그 추적

---

## Task 3.6: GraphQL API 추가 (선택) 🔄

**파일**: 신규 `app/graphql/` 디렉토리

**현재 문제**:
- REST API는 Over-fetching/Under-fetching 문제
- 프론트엔드에서 여러 API 호출 필요

**개선 전략**:
```python
# requirements.txt
strawberry-graphql[fastapi]>=0.200.0

# app/graphql/schema.py
import strawberry

@strawberry.type
class Space:
    id: str
    name: str
    explain: str
    scenes: List['Scene']
    viewers: List['User']

@strawberry.type
class Query:
    @strawberry.field
    async def space(self, id: str) -> Space:
        space = await space_service.get_with_relations(id)
        return Space.from_db(space)

schema = strawberry.Schema(query=Query)

# main.py
from strawberry.fastapi import GraphQLRouter
app.include_router(GraphQLRouter(schema), prefix="/graphql")
```

**체크리스트**:
- [ ] Strawberry GraphQL 설치
- [ ] GraphQL 스키마 정의
- [ ] Query 리졸버 구현
- [ ] Mutation 리졸버 구현
- [ ] DataLoader 패턴 적용 (N+1 방지)
- [ ] GraphQL Playground 활성화
- [ ] 인증 미들웨어 추가
- [ ] 성능 비교 (REST vs GraphQL)

**쿼리 예시**:
```graphql
query GetSpaceWithScenes {
  space(id: "507f1f77bcf86cd799439011") {
    name
    explain
    scenes {
      name
      links {
        target {
          name
        }
        coordinates {
          x, y, z
        }
      }
    }
    viewers {
      email
      role
    }
  }
}
```

---

## Task 3.7: 관리자 대시보드 구축 📊

**파일**: 신규 `app/admin/` 디렉토리

**현재 문제**:
- 시스템 모니터링 불가
- 사용자 관리 기능 없음
- 통계 확인 어려움

**개선 전략**:
```python
# requirements.txt
fastapi-admin>=1.0.0

# app/admin/views.py
from fastapi_admin.app import app as admin_app
from fastapi_admin.resources import Model

class UserAdmin(Model):
    model = User
    fields = ["userid", "email", "created_at"]
    search_fields = ["email"]

class SpaceAdmin(Model):
    model = Space
    fields = ["name", "creator", "created_at", "scene_count"]
    list_display = ["name", "creator", "scene_count"]

# main.py
app.mount("/admin", admin_app)
```

**체크리스트**:
- [ ] FastAPI Admin 또는 SQLAdmin 설치
- [ ] 관리자 인증 시스템 구축
- [ ] 사용자 관리 페이지
- [ ] 공간 관리 페이지
- [ ] 씬 관리 페이지
- [ ] 통계 대시보드 (가입자, 활성 공간 등)
- [ ] 로그 뷰어
- [ ] 시스템 헬스 체크
- [ ] 권한 기반 접근 제어 (RBAC)

**대시보드 기능**:
- 총 사용자 수, 일일 활성 사용자
- 공간 생성 추이 (차트)
- 스토리지 사용량
- API 응답 시간 모니터링

---

## Task 3.8: Docker 및 CI/CD 파이프라인 🚀

**파일**: `Dockerfile`, `.github/workflows/`, `docker-compose.yml`

**현재 문제**:
- 수동 배포 프로세스
- 환경 일관성 부족
- 테스트 자동화 없음

**개선 전략**:
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017/
    depends_on:
      - mongo
      - redis

  mongo:
    image: mongo:7
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine

volumes:
  mongo_data:
```

```yaml
# .github/workflows/ci.yml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**체크리스트**:
- [ ] `Dockerfile` 작성 (멀티스테이지 빌드)
- [ ] `docker-compose.yml` 작성
- [ ] `.dockerignore` 작성
- [ ] GitHub Actions CI 워크플로우 작성
- [ ] 자동 테스트 실행 설정
- [ ] 코드 커버리지 리포트
- [ ] 자동 배포 (CD) 설정
- [ ] 환경별 설정 분리 (dev, staging, prod)
- [ ] 헬스 체크 엔드포인트 추가
- [ ] 로그 수집 (ELK 스택 연동)

---

## 완료 기준 (Definition of Done)

✅ 모든 체크리스트 항목 완료
✅ 의존성 주입 패턴 전체 적용
✅ Service/Repository 계층 분리 완료
✅ API v2 출시 및 문서화
✅ 캐싱 시스템 안정화 (히트율 80%+)
✅ Docker 배포 가능
✅ CI/CD 파이프라인 작동
✅ 테스트 커버리지 80% 이상
✅ 성능 테스트 통과 (동시 100명 사용자)
✅ 코드 리뷰 및 아키텍처 리뷰 완료
✅ Git 태그 (`v1.0.0-stable`)

---

## 예상 소요 시간
- Task 3.1: 12시간 (의존성 주입)
- Task 3.2: 16시간 (Service 계층)
- Task 3.3: 8시간 (API 버전 관리)
- Task 3.4: 10시간 (캐싱)
- Task 3.5: 8시간 (이벤트 시스템)
- Task 3.6: 12시간 (GraphQL, 선택)
- Task 3.7: 10시간 (관리자 대시보드)
- Task 3.8: 12시간 (Docker/CI/CD)
- **총계**: 88시간 (약 11일, GraphQL 포함 시 ~2.5주)

---

## 우선순위 내 세부 순서
1. **Task 3.1 + 3.2** (의존성 주입 + Service 계층) - 필수, 함께 진행
2. **Task 3.4** (캐싱) - 성능 향상 즉시 체감
3. **Task 3.8** (Docker/CI/CD) - 배포 자동화
4. **Task 3.3** (API 버전 관리) - 안정성 확보
5. **Task 3.5** (이벤트) - 확장성 준비
6. **Task 3.7** (대시보드) - 운영 편의성
7. **Task 3.6** (GraphQL) - 선택사항
