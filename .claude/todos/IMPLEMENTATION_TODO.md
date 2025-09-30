# Simulverse 실제 작업 TODO 리스트 🚀

> **작업 순서**: Priority 1 보안/성능 개선 → POI 기능 구현
> **총 예상 기간**: 약 10-12일

---

## 📋 Phase 0: Priority 1 - 보안 및 성능 개선 (1.5일)

### Task 0.1: 권한 검증 로직 수정 ⚠️ [2시간]
**파일**: `app/core/routers/space.py`

- [ ] `space.py:149` 권한 로직 수정
  ```python
  # 현재: if space.viewers[str(auth_user.id)] == 'Editor' or str(auth_user.id) in space.viewers:
  # 수정: user_id = str(auth_user.id)
  #       if user_id in space.viewers and space.viewers[user_id] == 'Editor':
  ```
- [ ] `space.py:24-31` 뷰어 권한 검증 강화
- [ ] `space.py:220` 업데이트 권한 체크 추가
- [ ] 권한 검증 단위 테스트 작성
- [ ] Viewer vs Editor 권한 테스트 (curl 또는 postman)

---

### Task 0.2: MongoDB 인덱스 추가 📊 [3시간]
**파일**: `manage/create_indexes.py` (신규)

- [ ] `manage/create_indexes.py` 스크립트 생성
- [ ] 인덱스 생성 코드 작성:
  ```python
  await db.users.create_index("email", unique=True)
  await db.spaces.create_index("creator")
  await db.spaces.create_index("viewers")
  await db.scenes.create_index("image_id")
  await db.links.create_index("target_id")
  ```
- [ ] 인덱스 적용 전후 성능 측정 (explain())
- [ ] README에 인덱스 설정 가이드 추가
- [ ] `db_setup.py`에 인덱스 생성 통합

---

### Task 0.3: ObjectId 검증 강화 🔐 [1.5시간]
**파일**: `app/core/libs/utils.py`, 각 라우터

- [ ] `utils.py`에 `validate_object_id()` 함수 추가
  ```python
  from bson.errors import InvalidId

  def validate_object_id(id_str: str) -> ObjectId:
      try:
          return ObjectId(id_str)
      except InvalidId:
          raise HTTPException(status_code=400, detail="Invalid ID format")
  ```
- [ ] `space.py`의 모든 ObjectId 변환에 적용
- [ ] `create.py`의 ObjectId 변환에 적용
- [ ] `asset.py`의 ObjectId 변환에 적용
- [ ] 400 Bad Request 테스트

---

### Task 0.4: 예외 처리 세분화 🛡️ [2시간]
**파일**: `app/main.py`, `app/core/templates/error.html`

- [ ] `main.py:50` 예외 핸들러 세분화
  ```python
  @app.exception_handler(HTTPException)
  async def http_exception_handler(request: Request, exc: HTTPException):
      if exc.status_code == 401:
          return RedirectResponse("/login/?error=unauthorized")
      elif exc.status_code == 403:
          return templates.TemplateResponse("error.html", {...})
      # ...
  ```
- [ ] `error.html` 템플릿 동적 렌더링 지원 (코드별 메시지)
- [ ] 403 Forbidden 전용 응답 추가
- [ ] 404 Not Found 전용 응답 추가
- [ ] 500 Server Error 로깅 추가
- [ ] 각 상황별 수동 테스트

---

### Task 0.5: 비밀번호 해싱 중복 제거 🔧 [1시간]
**파일**: `app/core/models/auth_manager.py`, `database.py`

- [ ] `auth_manager.py:16` CryptContext 제거
- [ ] `utils.py`의 `pwd_context` 사용하도록 통일
- [ ] import 경로 정리
- [ ] 순환 참조 방지 확인
- [ ] 기존 해싱 동작 검증 (로그인 테스트)

---

## 🎯 Phase 1: POI 시스템 - DB 스키마 및 백엔드 (2일)

### Task 1.1: POI 데이터 모델 생성 [3시간]
**파일**: `app/core/schemas/poi_model.py` (신규)

- [ ] `poi_model.py` 생성
  ```python
  class POIBase(BaseModel):
      type: str  # "info" | "link" | "media"
      title: str
      description: Optional[str] = None
      position: dict  # {x, y, z}
      rotation: dict = {"x": 0, "y": 0, "z": 0}
      scale: dict = {"x": 1, "y": 1, "z": 1}
      visible: bool = True
      image_id: Optional[ObjectId] = None
      target_scene_id: Optional[ObjectId] = None
  ```
- [ ] `CreatePOIForm` 폼 검증 클래스 작성
- [ ] Pydantic 스키마 검증 테스트

---

### Task 1.2: Database POI 메서드 추가 [4시간]
**파일**: `app/core/models/database.py`

- [ ] `create_poi(scene_id, poi_data)` 메서드 추가
  ```python
  async def create_poi(self, scene_id: ObjectId, poi_data: dict) -> ObjectId:
      poi_data['poi_id'] = ObjectId()
      poi_data['created_at'] = datetime.utcnow()
      await self.db.scenes.update_one(
          {"_id": scene_id},
          {"$push": {"pois": poi_data}}
      )
      return poi_data['poi_id']
  ```
- [ ] `update_poi(scene_id, poi_id, update_data)` 메서드 추가
- [ ] `delete_poi(scene_id, poi_id)` 메서드 추가
- [ ] `get_pois(scene_id)` 메서드 추가
- [ ] 메서드별 단위 테스트 작성

---

### Task 1.3: POI 라우터 생성 [4시간]
**파일**: `app/core/routers/poi.py` (신규)

- [ ] `poi.py` 라우터 파일 생성
- [ ] POST `/space/poi/create/{scene_id}` 구현
  - [ ] 권한 검증 (Editor만 생성 가능)
  - [ ] 이미지 업로드 처리 (GridFS)
  - [ ] POI 데이터 생성
- [ ] PUT `/space/poi/update/{scene_id}/{poi_id}` 구현
- [ ] DELETE `/space/poi/delete/{scene_id}/{poi_id}` 구현
- [ ] GET `/space/pois/{scene_id}` 구현 (모든 POI 조회)
- [ ] GET `/space/scenes/{space_id}` 구현 (링크용 씬 목록)
- [ ] `main.py`에 라우터 등록
  ```python
  from .core.routers import poi
  app.include_router(poi.router)
  ```
- [ ] Postman/curl로 API 테스트

---

### Task 1.4: MongoDB 마이그레이션 [1시간]
**파일**: `manage/migrate_add_pois.py` (신규)

- [ ] 마이그레이션 스크립트 생성
  ```python
  async def migrate():
      await db.scenes.update_many(
          {"pois": {"$exists": False}},
          {"$set": {"pois": []}}
      )
  ```
- [ ] 기존 scenes에 `pois: []` 필드 추가
- [ ] 마이그레이션 실행 및 검증
- [ ] README에 마이그레이션 가이드 추가

---

## 🎨 Phase 1.5: 사용자 입력 UI - 모달 창 (1일)

### Task 1.5.1: 모달 CSS 작성 [2시간]
**파일**: `app/core/static/css/poi-modal.css` (신규)

- [ ] `poi-modal.css` 파일 생성
- [ ] 모달 오버레이 스타일 (반투명 배경)
- [ ] 모달 컨테이너 스타일 (중앙 정렬)
- [ ] 폼 입력 필드 스타일
- [ ] 이미지 업로드 드래그 앤 드롭 영역 스타일
- [ ] 버튼 스타일 (Primary, Secondary, Cancel)
- [ ] 로딩 애니메이션 (스피너)
- [ ] 모바일 반응형 디자인 (@media)
- [ ] `scene.html`에 CSS 링크 추가

---

### Task 1.5.2: 모달 JavaScript 구현 [4시간]
**파일**: `app/core/static/scripts/poi-editor.js` (수정)

- [ ] `showPOIModal(type)` 함수 구현
  - [ ] 완전한 HTML 모달 구조 생성
  - [ ] type='info'인 경우: 제목, 설명, 이미지 필드
  - [ ] type='link'인 경우: 제목, 타겟 씬 선택
  - [ ] 좌표 입력 필드 (X, Y, Z) + "현재 위치 사용" 버튼
- [ ] `setupModalEvents()` 함수 구현
  - [ ] 이미지 파일 선택 이벤트
  - [ ] 드래그 앤 드롭 이벤트 (dragover, drop)
  - [ ] "현재 위치 사용" 버튼 클릭 (좌표 재계산)
  - [ ] "저장" 버튼 클릭 (폼 검증 + API 호출)
  - [ ] "취소" 버튼 클릭 (모달 닫기)
  - [ ] ESC 키로 모달 닫기
- [ ] `previewImage(file)` 함수 구현
  - [ ] 이미지 미리보기 표시
  - [ ] 파일 크기 검증 (10MB 제한)
  - [ ] 파일 형식 검증 (jpg, png)
- [ ] `getCurrentCursorPosition()` 함수 구현
  - [ ] Raycaster로 현재 시점 좌표 계산
  - [ ] 입력 필드에 좌표 자동 채우기
- [ ] 폼 검증 로직
  - [ ] 제목 필수 체크
  - [ ] 이미지 크기 체크
  - [ ] 좌표 유효성 체크
- [ ] 테스트
  - [ ] Info POI 모달 동작
  - [ ] Link POI 모달 동작
  - [ ] 드래그 앤 드롭
  - [ ] 이미지 미리보기

---

### Task 1.5.3: 씬 선택 드롭다운 [2시간]
**파일**: `poi-editor.js` (계속)

- [ ] `/space/scenes/{space_id}` API 호출
- [ ] 동적 `<select>` 옵션 생성
  ```javascript
  scenes.forEach(scene => {
      option.value = scene._id;
      option.textContent = scene.name;
  });
  ```
- [ ] 현재 씬은 선택 불가 처리
- [ ] 씬 썸네일 표시 (선택)
- [ ] 링크 POI 모달에서 씬 선택 테스트

---

## 🌐 Phase 2: A-Frame 컴포넌트 구현 (2-3일)

### Task 2.1: POI 마커 컴포넌트 [6시간]
**파일**: `app/core/static/scripts/poi-marker.js` (신규)

- [ ] `poi-marker.js` 파일 생성
- [ ] `AFRAME.registerComponent('poi-marker', {...})` 작성
  - [ ] Schema 정의 (poiId, type, title, description, imageUrl, targetSceneId)
  - [ ] `init()` 메서드: 마커 생성
    - [ ] type='info': 🔵 파란색 구체
    - [ ] type='link': 🟢 녹색 구체 + 화살표
  - [ ] `createMarker()` 메서드: 3D 마커 엔티티 생성
  - [ ] `setupInteractions()` 메서드: 클릭 이벤트
    - [ ] Info: 상세 패널 표시
    - [ ] Link: 씬 이동
  - [ ] Hover 효과 (마우스 오버 시 크기 증가)
- [ ] VR 컨트롤러 지원 (선택)
- [ ] 마커 테스트 (scene.html에 더미 데이터)

---

### Task 2.2: 반응형 패널 컴포넌트 [4시간]
**파일**: `app/core/static/scripts/responsive-panel.js` (신규)

- [ ] `responsive-panel.js` 파일 생성
- [ ] `AFRAME.registerComponent('responsive-panel', {...})` 작성
  - [ ] Schema 정의 (title, description, imageUrl, width, height)
  - [ ] `init()`: 패널 생성 (a-plane + 텍스트 + 이미지)
  - [ ] `tick()`: 거리 기반 스케일 조정
    ```javascript
    const distance = camera.position.distanceTo(this.el.position);
    const scale = Math.max(0.5, Math.min(2, distance / 3));
    ```
  - [ ] Look-at 카메라 (항상 카메라 방향)
  - [ ] 투명도 조정 (거리에 따라 페이드)
  - [ ] 닫기 버튼 (X 버튼)
- [ ] 패널 애니메이션 (등장/사라짐)
- [ ] 모바일 터치 이벤트
- [ ] 패널 테스트

---

### Task 2.3: POI 편집기 컴포넌트 (완성) [6시간]
**파일**: `app/core/static/scripts/poi-editor.js` (수정)

- [ ] `AFRAME.registerComponent('poi-editor', {...})` 작성
  - [ ] Schema: `enabled: false`
  - [ ] `init()`: 키보드 이벤트 리스너
    - [ ] 'I' 키: Info POI 추가 모드
    - [ ] 'L' 키: Link POI 추가 모드
    - [ ] 'E' 키: 편집 모드 토글
    - [ ] 'Delete' 키: 선택된 POI 삭제
- [ ] `onKeyPress(event)` 핸들러
- [ ] `addInfoPOI()` 메서드
  - [ ] Raycaster로 교차점 계산
  - [ ] 모달 창 표시 (Phase 1.5에서 구현)
  - [ ] 서버 API 호출 (fetch POST)
  - [ ] 성공 시 실시간 마커 렌더링
- [ ] `addLinkPOI()` 메서드
- [ ] `deletePOI(poi_id)` 메서드
- [ ] `refreshPOIs()` 메서드 (서버에서 최신 POI 로드)
- [ ] 편집 모드 UI 인디케이터 (우측 상단)
- [ ] 편집기 통합 테스트

---

## 🎨 Phase 3: 템플릿 및 UI 통합 (1일)

### Task 3.1: scene.html 수정 [3시간]
**파일**: `app/core/templates/aframe/scene.html`

- [ ] POI 데이터를 Jinja2로 전달 (space.py 라우터 수정)
  ```python
  pois = await db_manager.get_pois(scene_id)
  return templates.TemplateResponse("aframe/scene.html", {
      "pois": pois,
      ...
  })
  ```
- [ ] POI 렌더링 루프 추가
  ```html
  {% for poi in pois %}
  <a-entity poi-marker="
    poiId: {{ poi.poi_id }};
    type: {{ poi.type }};
    title: {{ poi.title }};
    ...">
  </a-entity>
  {% endfor %}
  ```
- [ ] 스크립트 import
  ```html
  <script src="/static/scripts/poi-marker.js"></script>
  <script src="/static/scripts/responsive-panel.js"></script>
  <script src="/static/scripts/poi-editor.js"></script>
  <link rel="stylesheet" href="/static/css/poi-modal.css">
  ```
- [ ] 편집 모드 컴포넌트 추가
  ```html
  <a-entity poi-editor="enabled: {{ 'true' if is_editor else 'false' }}"></a-entity>
  ```
- [ ] 편집 모드 안내 메시지 (키보드 단축키)
- [ ] 권한에 따라 편집 UI 표시/숨김

---

### Task 3.2: 공간 목록/관리 UI [2시간]
**파일**: `app/core/templates/home.html` 또는 `space_list.html`

- [ ] 공간 목록에 POI 개수 표시
  ```python
  space['poi_count'] = len(space.get('pois', []))
  ```
- [ ] 공간 상세 페이지에 POI 목록 표시
- [ ] POI 관리 섹션 (편집자 전용)
- [ ] POI 통계 (Info vs Link 개수)
- [ ] CSS 스타일링

---

### Task 3.3: 모바일 반응형 최적화 [3시간]
**파일**: 각 CSS, JavaScript 파일

- [ ] 모달 창 모바일 레이아웃
- [ ] 터치 이벤트 지원
- [ ] POI 마커 크기 조정 (모바일)
- [ ] 패널 크기 조정 (모바일)
- [ ] 키보드 대신 버튼 UI (모바일)
- [ ] 드래그 앤 드롭 → 파일 선택 대체
- [ ] 모바일 브라우저 테스트 (iOS Safari, Android Chrome)

---

## 🧪 Phase 4: 테스트 및 최적화 (1-2일)

### Task 4.1: 기능 테스트 [4시간]
- [ ] Info POI 추가/수정/삭제 테스트
  - [ ] 이미지 업로드 포함
  - [ ] 설명 긴 텍스트 (1000자)
- [ ] Link POI 추가/수정/삭제 테스트
  - [ ] 다른 씬으로 이동 확인
  - [ ] 순환 링크 테스트
- [ ] 권한 검증 테스트
  - [ ] Viewer는 POI 추가 불가
  - [ ] Editor만 POI CRUD 가능
  - [ ] 로그아웃 상태에서 접근 불가
- [ ] 에러 핸들링 테스트
  - [ ] 잘못된 ObjectId
  - [ ] 큰 이미지 업로드
  - [ ] 필수 필드 누락

---

### Task 4.2: 성능 테스트 [3시간]
- [ ] 20개 이상 POI 렌더링 테스트
  - [ ] FPS 측정 (목표: 60fps 이상)
  - [ ] 메모리 사용량
- [ ] 모바일 성능 테스트
  - [ ] iOS Safari
  - [ ] Android Chrome
  - [ ] 저사양 디바이스
- [ ] VR 헤드셋 테스트 (선택)
  - [ ] Oculus Quest
  - [ ] HTC Vive
- [ ] 최적화
  - [ ] 원거리 POI 컬링 (보이지 않으면 숨기기)
  - [ ] LOD (Level of Detail) 적용
  - [ ] 이미지 레이지 로딩

---

### Task 4.3: 버그 수정 및 문서화 [3시간]
- [ ] 발견된 버그 수정
- [ ] 사용자 매뉴얼 작성
  - [ ] POI 추가 방법
  - [ ] 키보드 단축키 설명
  - [ ] 이미지 업로드 가이드
- [ ] 개발자 문서 업데이트
  - [ ] API 명세서
  - [ ] 데이터베이스 스키마
  - [ ] 컴포넌트 아키텍처
- [ ] README 업데이트
  - [ ] 새 기능 소개
  - [ ] 스크린샷/GIF
  - [ ] 설치 및 사용법

---

## ✅ 최종 체크리스트

### Priority 1 완료 확인
- [ ] 모든 보안 이슈 해결
- [ ] MongoDB 인덱스 적용 및 성능 개선 확인
- [ ] 예외 처리 세분화 완료
- [ ] 모든 ObjectId 검증 적용
- [ ] 비밀번호 해싱 중복 제거
- [ ] Git 커밋: `git commit -m "feat: Priority 1 security and performance fixes"`
- [ ] Git 태그: `git tag v0.2.0-security-fixes`

### POI 시스템 완료 확인
- [ ] Backend API 모든 엔드포인트 동작
- [ ] A-Frame 컴포넌트 정상 렌더링
- [ ] 모달 UI 완전 동작
- [ ] 모바일 반응형 확인
- [ ] 권한 시스템 정상 동작
- [ ] 성능 목표 달성 (60fps)
- [ ] 문서화 완료
- [ ] Git 커밋: `git commit -m "feat: POI system implementation"`
- [ ] Git 태그: `git tag v0.3.0-poi-system`

### 배포 준비
- [ ] 테스트 데이터 생성 (`db_setup.py` 실행)
- [ ] 프로덕션 환경 변수 확인 (`/etc/environment`)
- [ ] 로그 레벨 확인 (프로덕션: INFO)
- [ ] 디버그 모드 비활성화
- [ ] 백업 스크립트 준비
- [ ] 롤백 계획 수립
- [ ] 배포 후 모니터링 (1주일)

---

## 📅 예상 일정

| Phase | 작업 | 예상 시간 | 누적 |
|-------|------|----------|------|
| 0.1 | 권한 검증 수정 | 2h | 2h |
| 0.2 | MongoDB 인덱스 | 3h | 5h |
| 0.3 | ObjectId 검증 | 1.5h | 6.5h |
| 0.4 | 예외 처리 | 2h | 8.5h |
| 0.5 | 해싱 중복 제거 | 1h | 9.5h (1.5일) |
| 1.1 | POI 모델 | 3h | 12.5h |
| 1.2 | Database 메서드 | 4h | 16.5h |
| 1.3 | POI 라우터 | 4h | 20.5h |
| 1.4 | 마이그레이션 | 1h | 21.5h (2.5일) |
| 1.5.1 | 모달 CSS | 2h | 23.5h |
| 1.5.2 | 모달 JS | 4h | 27.5h |
| 1.5.3 | 씬 선택 | 2h | 29.5h (3.5일) |
| 2.1 | POI 마커 | 6h | 35.5h |
| 2.2 | 반응형 패널 | 4h | 39.5h |
| 2.3 | POI 편집기 | 6h | 45.5h (5.5일) |
| 3.1 | scene.html | 3h | 48.5h |
| 3.2 | 관리 UI | 2h | 50.5h |
| 3.3 | 모바일 최적화 | 3h | 53.5h (6.5일) |
| 4.1 | 기능 테스트 | 4h | 57.5h |
| 4.2 | 성능 테스트 | 3h | 60.5h |
| 4.3 | 버그 수정/문서화 | 3h | 63.5h (8일) |

**총 예상 시간**: 약 64시간 (8일)
**버퍼 포함**: 10-12일 (예상치 못한 버그, 리팩토링 시간 포함)

---

## 🎯 성공 지표

### 보안 개선
- ✅ 권한 우회 공격 방어
- ✅ 모든 입력 검증 적용
- ✅ 적절한 에러 메시지 (정보 노출 방지)

### 성능 개선
- ✅ 사용자 조회: 500ms → 5ms (100배)
- ✅ 공간 목록: 200ms → 20ms (10배)
- ✅ POI 20개 렌더링: 60fps 유지

### 사용성 개선
- ✅ POI 추가 3클릭 이내
- ✅ 모바일에서 원활한 동작
- ✅ 직관적인 UI (사용자 매뉴얼 없이 사용 가능)

---

## 🚀 다음 단계 (이후 작업)

완료 후 검토할 항목:
1. Priority 2 작업 (N+1 쿼리 해결, API 표준화)
2. Priority 3 작업 (Redis 캐싱, GraphQL)
3. POI 고급 기능 (애니메이션, 오디오 POI, 비디오 POI)
4. 멀티플레이어 기능 (실시간 협업 편집)

---

**작성일**: 2025-09-30
**버전**: v1.0
**작성자**: Claude Code Assistant
