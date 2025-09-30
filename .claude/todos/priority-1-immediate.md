# Priority 1: 즉시 개선 (Immediate) 🚨

> **목표**: 보안 취약점 및 크리티컬 버그 수정
> **기간**: 1-2일
> **영향도**: Critical

---

## Task 1.1: 권한 검증 로직 수정 ⚠️

**파일**: `app/core/routers/space.py:149`

**현재 문제**:
```python
if space.viewers[str(auth_user.id)] == 'Editor' or str(auth_user.id) in space.viewers:
```
- `or` 조건으로 인해 두 번째 조건이 항상 True가 될 수 있음
- Editor 권한이 아닌 사용자도 수정 가능

**개선 전략**:
```python
# 수정 후
user_id = str(auth_user.id)
if user_id in space.viewers and space.viewers[user_id] == 'Editor':
```

**체크리스트**:
- [ ] `space.py:149` 권한 로직 수정
- [ ] `space.py:24-31` 뷰어 권한 검증 강화
- [ ] `space.py:220` 업데이트 권한 체크 추가
- [ ] 권한 검증 단위 테스트 작성
- [ ] Viewer vs Editor 권한 매트릭스 문서화

**검증 방법**:
```bash
# Viewer 계정으로 편집 시도 (실패해야 함)
curl -X POST /space/edit/{space_id} -H "Cookie: access_token=viewer_token"
```

---

## Task 1.2: MongoDB 인덱스 추가 📊

**파일**: 신규 `manage/create_indexes.py`

**현재 문제**:
- `users` 컬렉션의 email 조회 시 Full Scan
- `spaces` 컬렉션의 creator 조회 비효율

**개선 전략**:
```python
# 추가할 인덱스
await db.users.create_index("email", unique=True)
await db.spaces.create_index("creator")
await db.spaces.create_index("viewers")
await db.scenes.create_index("image_id")
```

**체크리스트**:
- [ ] `manage/create_indexes.py` 스크립트 생성
- [ ] users.email 유니크 인덱스 생성
- [ ] spaces.creator 인덱스 생성
- [ ] spaces.viewers 멀티키 인덱스 생성
- [ ] scenes.image_id 인덱스 생성
- [ ] links.target_id 인덱스 생성
- [ ] 인덱스 적용 전후 성능 측정 (explain())
- [ ] README에 인덱스 설정 가이드 추가

**예상 성능 개선**:
- 사용자 조회: 500ms → 5ms (100배)
- 공간 목록 조회: 200ms → 20ms (10배)

---

## Task 1.3: 예외 처리 세분화 🛡️

**파일**: `app/main.py:50`

**현재 문제**:
```python
@app.exception_handler(HTTPException)
async def unicorn_exception_handler(request: Request, exc: HTTPException):
    response = RedirectResponse("/login/?errors=401", status_code=status.HTTP_302_FOUND)
    return response
```
- 모든 HTTP 예외를 401로 처리
- 403(권한 없음), 404(없음), 500(서버 오류) 구분 불가

**개선 전략**:
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse("/login/?error=unauthorized")
    elif exc.status_code == 403:
        return templates.TemplateResponse("error.html",
            {"request": request, "error": "Access Denied", "code": 403})
    elif exc.status_code == 404:
        return templates.TemplateResponse("error.html",
            {"request": request, "error": "Not Found", "code": 404})
    else:
        # 500 등 기타 오류
        logger.error(f"Unhandled exception: {exc.detail}")
        return templates.TemplateResponse("error.html",
            {"request": request, "error": "Server Error", "code": 500})
```

**체크리스트**:
- [ ] `main.py` 예외 핸들러 세분화
- [ ] `error.html` 템플릿 동적 렌더링 지원
- [ ] 403 Forbidden 전용 응답 추가
- [ ] 404 Not Found 전용 응답 추가
- [ ] 500 Server Error 로깅 추가
- [ ] 각 라우터에서 적절한 예외 발생 확인
- [ ] 보안 정보 노출 방지 검증

---

## Task 1.4: ObjectId 검증 강화 🔐

**파일**: `app/core/routers/space.py` (여러 위치)

**현재 문제**:
```python
space_id = ObjectId(space_id)  # 잘못된 형식 입력 시 크래시
```

**개선 전략**:
```python
from bson.errors import InvalidId

def validate_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# 사용
space_id = validate_object_id(space_id)
```

**체크리스트**:
- [ ] `app/core/libs/utils.py`에 validate_object_id 함수 추가
- [ ] `space.py`의 모든 ObjectId 변환에 적용
- [ ] `create.py`의 ObjectId 변환에 적용
- [ ] `asset.py`의 ObjectId 변환에 적용
- [ ] 400 Bad Request 응답 테스트
- [ ] 에러 메시지 사용자 친화적으로 변경

---

## Task 1.5: 비밀번호 해싱 중복 제거 🔧

**파일**: `app/core/models/database.py:57`

**현재 문제**:
- `utils.py`와 `database.py` 모두에서 bcrypt 컨텍스트 생성
- `auth_manager.py`에도 CryptContext 중복

**개선 전략**:
```python
# utils.py에서 단일 인스턴스 관리
from app.core.libs.utils import verify_password, get_password_hash

# 모든 파일에서 import하여 사용
```

**체크리스트**:
- [ ] `auth_manager.py:16` CryptContext 제거
- [ ] `utils.py`의 pwd_context 사용하도록 통일
- [ ] import 경로 정리
- [ ] 순환 참조 방지 확인
- [ ] 기존 해싱 동작 동일성 검증

---

## 완료 기준 (Definition of Done)

✅ 모든 체크리스트 항목 완료
✅ 수동 테스트 통과 (권한, 예외, ID 검증)
✅ 성능 테스트 완료 (인덱스 효과 측정)
✅ 코드 리뷰 완료
✅ Git 커밋 및 태그 (`v0.2.0-security-fixes`)

---

## 예상 소요 시간
- Task 1.1: 2시간
- Task 1.2: 3시간
- Task 1.3: 2시간
- Task 1.4: 1.5시간
- Task 1.5: 1시간
- **총계**: 9.5시간 (약 1.5일)
