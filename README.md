# simulverse
<p align="center">
    <em> A metaverse content management framework based on fastapi </em>
</p>

# Prerequisite

## Environment Setup

Simulverse uses system environment variables for configuration. Add the following to `/etc/environment`:

```bash
MONGODB_URL="mongodb://id:pw@mongo1:27017/"
MONGODB_DATABASE="simulverse"
JWT_SECRET_KEY="your-secret-key-here"
JWT_REFRESH_SECRET_KEY="your-refresh-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
```

After editing `/etc/environment`, reload environment variables:
```bash
source /etc/environment
# OR restart your session/system
```

### Alternative: Local Development with .env
For local development, you can optionally create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your local settings
```

**Priority**: System environment variables (`/etc/environment`) take precedence over `.env` file.

# Quick Start

## 0. MongoDB Index Setup
```bash
cd manage
python create_indexes.py
```

이 스크립트는 핵심 컬렉션(users, spaces, scenes, links)에 필요한 인덱스를 생성합니다.
`manage/db_setup.py` 실행 시 자동으로 호출되지만, 스키마 변경 후에는 별도로 실행해 인덱스를 갱신할 수 있습니다.

## 1. Database Setup (테스트 데이터 생성)
```bash
cd manage
python db_setup.py
```

이 스크립트는 다음을 자동으로 생성합니다:
- 👥 테스트 사용자 2명 (editor@test.com, viewer@test.com)
- 🏛️ 샘플 공간 2개 (테스트 박물관, 현대 갤러리)
- 🎬 씬 4개 (360도 이미지 포함)
- 📍 POI 5개 (정보 마커)
- 🔗 씬 간 링크 5개

**테스트 계정:**
- Email: `editor@test.com` / Password: `test1234`
- Email: `viewer@test.com` / Password: `test1234`

## 2. POI 추가 및 관리 가이드
1. 웹앱을 실행하고 `editor@test.com / test1234` 계정으로 로그인합니다.
2. `/view/`에서 원하는 공간을 선택하고 씬 편집 페이지(`/space/scene/edit/{space_id}/{scene_id}`)로 이동합니다.
3. `Points of Interest` 테이블 우측 상단의 `POI 추가` 버튼을 눌러 모달에서 타입, 제목, 좌표 등을 입력하고 저장합니다.
4. 생성된 POI는 테이블에서 확인할 수 있으며, 필요 시 `삭제` 버튼으로 제거할 수 있습니다.
5. 씬 뷰(`/space/scene/{space_id}/{scene_id}`)에 접속하면 방금 추가한 POI가 A-Frame 마커로 표시됩니다.

**Tip**
- 링크 POI는 `타겟 씬`을 지정하면 다른 씬으로 이동하는 포털이 됩니다.
- 좌표/회전 값을 조정해 마커 위치를 세밀하게 배치할 수 있습니다.

## 3. Database Drop (데이터 삭제)
⚠️ 주의: 모든 데이터가 삭제됩니다!
```bash
cd manage
python db_drop.py
```

# How to Execute
 - HTTPS support
```python
>$ python simulverse.py https
```
 - HTTP support
 ```python
>$ python simulverse.py http
```

# Project Structure
```
📦app
 ┣ 📂core
 ┃ ┣ 📂instance
 ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┗ 📜config.py
 ┃ ┣ 📂libs
 ┃ ┃ ┣ 📜oauth2_cookie.py
 ┃ ┃ ┣ 📜pyobjectid.py
 ┃ ┃ ┣ 📜resolve_error.py
 ┃ ┃ ┗ 📜utils.py
 ┃ ┣ 📂models
 ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┣ 📜auth_manager.py
 ┃ ┃ ┗ 📜database.py
 ┃ ┣ 📂routers
 ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┣ 📜asset.py
 ┃ ┃ ┣ 📜create.py
 ┃ ┃ ┣ 📜login.py
 ┃ ┃ ┣ 📜page_view.py
 ┃ ┃ ┣ 📜register.py
 ┃ ┃ ┗ 📜space.py
 ┃ ┣ 📂schemas
 ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┣ 📜space_model.py
 ┃ ┃ ┣ 📜token_model.py
 ┃ ┃ ┗ 📜user_model.py
 ┃ ┣ 📂templates
 ┃ ┃ ┣ 📂aframe
 ┃ ┃ ┃ ┣ 📜scene.html
 ┃ ┃ ┃ ┗ 📜view_scenes.html
 ┃ ┃ ┣ 📂auth
 ┃ ┃ ┃ ┣ 📜login.html
 ┃ ┃ ┃ ┗ 📜register.html
 ┃ ┃ ┣ 📂include
 ┃ ┃ ┃ ┣ 📜alerts.html
 ┃ ┃ ┃ ┣ 📜sidebar.html
 ┃ ┃ ┃ ┣ 📜topnav-sidebar.html
 ┃ ┃ ┃ ┗ 📜topnav.html
 ┃ ┃ ┣ 📂space
 ┃ ┃ ┃ ┣ 📜create_scene.html
 ┃ ┃ ┃ ┣ 📜create_space.html
 ┃ ┃ ┃ ┣ 📜update_scene.html
 ┃ ┃ ┃ ┣ 📜update_space.html
 ┃ ┃ ┃ ┗ 📜view_space.html
 ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┣ 📜base.html
 ┃ ┃ ┣ 📜error.html
 ┃ ┃ ┗ 📜page.html
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜settings.py
 ┣ 📂static
 ┃ ┣ 📂css
 ┃ ┃ ┗ 📜custom_style.css
 ┃ ┣ 📂images
 ┃ ┃ ┗ 📜favicon.png
 ┃ ┗ 📂scripts
 ┃ ┃ ┣ 📜contents-save.js
 ┃ ┃ ┣ 📜dynamic_fields.js
 ┃ ┃ ┗ 📜link-controls.js
 ┣ 📜__init__.py
 ┗ 📜main.py
```

## `core/libs`
 - contains utility libraries

## `core/models`
 - drivers for database
 - dirvers for authentication

## `core/routers`
 - Contains routing map

## `core/schemas`
 - Contains database schemas

## `core/templates`
 - Continas jinja2 templates

## `core/static`
 - Contains css, images, and javascripts files.

---

# Management Scripts (`manage/`)

데이터베이스 관리를 위한 유틸리티 스크립트:

| 스크립트 | 설명 |
|---------|------|
| `db_setup.py` | 테스트 데이터 자동 생성 (사용자, 공간, 씬, POI) |
| `db_drop.py` | 데이터베이스 전체 삭제 (안전 확인 포함) |
| `db_check_users.py` | 사용자 목록 조회 |
| `db_check_space.py` | 공간 목록 조회 |
| `db_check_scene.py` | 씬 목록 조회 |
| `db_check_link.py` | 링크 목록 조회 |
| `db_check_asset.py` | GridFS 이미지 목록 조회 |

**사용 예시:**
```bash
cd manage

# 테스트 데이터 생성
python db_setup.py

# 사용자 확인
python db_check_users.py

# 데이터베이스 삭제 (주의!)
python db_drop.py
```

---

# Development Roadmap

개선 계획 및 개발 전략은 [`.claude/todos/`](.claude/todos/) 폴더를 참고하세요:

- 📋 [ROADMAP.md](.claude/todos/ROADMAP.md) - 전체 개선 로드맵
- 🚨 [priority-1-immediate.md](.claude/todos/priority-1-immediate.md) - 즉시 개선 (보안, 인덱스)
- ⚡ [priority-2-short-term.md](.claude/todos/priority-2-short-term.md) - 성능 최적화
- 🏗️ [priority-3-mid-term.md](.claude/todos/priority-3-mid-term.md) - 아키텍처 재설계
- 📍 [feature-poi-system.md](.claude/todos/feature-poi-system.md) - POI 시스템 개발 계획
- 🧪 [test-data-setup.md](.claude/todos/test-data-setup.md) - 테스트 데이터 준비
