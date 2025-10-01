# Simulverse

<p align="center">
    <em>A metaverse content management framework based on FastAPI and A-Frame</em>
</p>

<p align="center">
    <strong>🌐 360° VR Spaces | 📍 Interactive POIs | 🔗 Scene Navigation | 👥 Collaborative Editing</strong>
</p>

---

## ✨ Features

- **🎭 VR Scene Management**: Create and manage 360° panoramic spaces
- **📍 POI System**: Add interactive Points of Interest (Info, Link, Media)
- **🔗 Scene Navigation**: Connect multiple scenes with navigation links
- **👥 Role-Based Access**: Editor and Viewer permissions
- **🎨 A-Frame Integration**: WebVR experiences in the browser
- **🖼️ Asset Management**: GridFS-based image storage
- **🔒 Secure Authentication**: JWT-based auth with bcrypt password hashing

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

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Database Setup

### Create MongoDB Indexes (성능 최적화)
```bash
python3 manage/create_indexes.py
```

이 스크립트는 다음 인덱스를 생성합니다:
- `users.email` (unique)
- `spaces.creator`, `spaces.viewers`
- `scenes.image_id`
- `links.target_id`

### POI Field Migration (POI 시스템 활성화)
```bash
python3 manage/migrate_add_pois.py
```

기존 scenes에 `pois: []` 필드를 추가합니다.

### Test Data Setup (테스트 데이터 생성)
```bash
python3 manage/db_setup.py
```

이 스크립트는 다음을 자동으로 생성합니다:
- 👥 테스트 사용자 2명 (editor@test.com, viewer@test.com)
- 🏛️ 샘플 공간 2개 (테스트 박물관, 현대 갤러리)
- 🎬 씬 4개 (360도 이미지 포함)
- 📍 POI 5개 (정보 마커 포함)
- 🔗 씬 간 링크 5개

**테스트 계정:**
- Email: `editor@test.com` / Password: `test1234` (편집 권한)
- Email: `viewer@test.com` / Password: `test1234` (보기 권한)

## 3. Run Server

### HTTP (Development)
```bash
python simulverse.py http
```

### HTTPS (Production)
```bash
python simulverse.py https
```

서버 실행 후 브라우저에서 `http://localhost:8000` 접속

## 4. Database Drop (데이터 삭제)
⚠️ 주의: 모든 데이터가 삭제됩니다!
```bash
python3 manage/db_drop.py
```

# 📍 POI System Usage

POI (Point of Interest) 시스템을 사용하여 VR 씬에 인터랙티브 마커를 추가할 수 있습니다.

## POI Types

1. **Info POI** (🔵 Blue): 정보 표시 (텍스트, 이미지)
2. **Link POI** (🟢 Green): 다른 씬으로 이동
3. **Media POI** (🟣 Purple): 비디오/오디오 재생 (예정)

## Keyboard Shortcuts (Editor Only)

| Key | Action |
|-----|--------|
| `I` | Add Info POI |
| `L` | Add Link POI |
| `M` | Add Media POI |
| `E` | Toggle Edit Mode |
| `Del` | Delete Selected POI |
| `Esc` | Deselect POI |

## Workflow

1. VR 씬에 진입 (Editor 권한 필요)
2. `I` 키를 눌러 Info POI 모달 열기
3. 제목, 설명, 위치 입력
4. "Use Current Camera Position" 버튼으로 현재 위치 사용
5. 이미지 업로드 (선택사항, JPG/PNG, 최대 10MB)
6. "Create POI" 버튼 클릭
7. 씬에 3D 마커가 생성됨

## POI Interaction

- **Hover**: 툴팁 표시, 마커 확대
- **Click (Info POI)**: 상세 정보 패널 표시
- **Click (Link POI)**: 타겟 씬으로 이동
- **Edit Mode**: POI 선택 후 편집/삭제

# Project Structure

```
📦 simulverse/
├── 📂 app/
│   ├── 📂 core/
│   │   ├── 📂 libs/              # Utility libraries
│   │   │   ├── oauth2_cookie.py
│   │   │   ├── pyobjectid.py
│   │   │   └── utils.py          # Password hashing, ObjectId validation
│   │   ├── 📂 models/            # Database & Auth
│   │   │   ├── auth_manager.py   # JWT authentication
│   │   │   └── database.py       # MongoDB operations + POI methods
│   │   ├── 📂 routers/           # API endpoints
│   │   │   ├── space.py          # Space/Scene management
│   │   │   ├── poi.py            # ✨ POI CRUD endpoints
│   │   │   ├── asset.py          # Image serving (GridFS)
│   │   │   ├── create.py
│   │   │   ├── login.py
│   │   │   ├── register.py
│   │   │   └── page_view.py
│   │   ├── 📂 schemas/           # Pydantic models
│   │   │   ├── poi_model.py      # ✨ POI data models
│   │   │   ├── space_model.py
│   │   │   ├── token_model.py
│   │   │   └── user_model.py
│   │   ├── 📂 templates/         # Jinja2 templates
│   │   │   ├── 📂 aframe/
│   │   │   │   ├── scene.html    # ✨ VR scene with POIs
│   │   │   │   └── view_scenes.html
│   │   │   ├── 📂 auth/
│   │   │   ├── 📂 space/
│   │   │   └── error.html        # ✨ Dynamic error pages
│   │   └── config.py             # Settings
│   ├── 📂 static/
│   │   ├── 📂 css/
│   │   │   ├── custom_style.css
│   │   │   └── poi-modal.css     # ✨ POI modal styles
│   │   └── 📂 scripts/
│   │       ├── link-controls.js
│   │       ├── poi-editor.js              # ✨ Modal & form handling
│   │       ├── poi-editor-component.js    # ✨ A-Frame editor component
│   │       ├── poi-marker.js              # ✨ 3D marker component
│   │       └── responsive-panel.js        # ✨ Info panel component
│   └── main.py                   # FastAPI app
├── 📂 manage/                    # Database scripts
│   ├── create_indexes.py         # ✨ MongoDB indexes
│   ├── migrate_add_pois.py       # ✨ POI field migration
│   ├── db_setup.py               # Test data generator
│   ├── db_drop.py                # Database cleanup
│   └── db_check_*.py             # Data inspection
├── 📂 .claude/todos/             # Development roadmap
│   ├── ROADMAP.md
│   ├── IMPLEMENTATION_TODO.md    # ✨ Completed tasks
│   └── priority-*.md
├── simulverse.py                 # Entry point
└── README.md

✨ = New/Updated for POI System
```

## Directory Details

### `core/libs`
Utility libraries for authentication, validation, and helpers
- `utils.py`: Password hashing, ObjectId validation (`validate_object_id`)
- `oauth2_cookie.py`: Cookie-based OAuth2 implementation

### `core/models`
Database drivers and authentication managers
- `database.py`: MongoDB operations including POI CRUD methods
- `auth_manager.py`: JWT token generation and user authentication

### `core/routers`
API endpoint definitions
- `space.py`: Space and scene management, POI data injection
- `poi.py`: POI CRUD endpoints (create/read/update/delete)
- `asset.py`: GridFS image serving

### `core/schemas`
Pydantic models for data validation
- `poi_model.py`: POI types (Info/Link/Media), forms, validation
- `space_model.py`: Space and scene structures
- `user_model.py`: User authentication models

### `core/templates`
Jinja2 HTML templates
- `aframe/scene.html`: VR scene viewer with POI rendering

### `core/static`
Frontend assets (CSS, JavaScript)
- `css/poi-modal.css`: Modal and form styling
- `scripts/poi-*.js`: POI system components and editor

---

# Management Scripts (`manage/`)

데이터베이스 관리 및 마이그레이션 스크립트:

## Setup Scripts

| 스크립트 | 설명 | 실행 시기 |
|---------|------|----------|
| `create_indexes.py` | 성능 최적화 인덱스 생성 | 초기 설정 또는 배포 시 |
| `migrate_add_pois.py` | POI 필드 마이그레이션 | POI 시스템 활성화 시 |
| `db_setup.py` | 테스트 데이터 생성 (POI 포함) | 개발/테스트 환경 |
| `db_drop.py` | 데이터베이스 전체 삭제 | 초기화 필요 시 |

## Inspection Scripts

| 스크립트 | 설명 |
|---------|------|
| `db_check_users.py` | 사용자 목록 조회 |
| `db_check_space.py` | 공간 목록 조회 |
| `db_check_scene.py` | 씬 목록 조회 |
| `db_check_link.py` | 링크 목록 조회 |
| `db_check_asset.py` | GridFS 이미지 목록 조회 |

## Setup Workflow

```bash
cd manage

# 1. 인덱스 생성 (성능 최적화)
python3 create_indexes.py

# 2. POI 필드 마이그레이션
python3 migrate_add_pois.py

# 3. 테스트 데이터 생성
python3 db_setup.py

# 4. 데이터 확인
python3 db_check_users.py
python3 db_check_space.py
```

---

# API Endpoints

## POI Management

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `POST` | `/space/poi/create/{scene_id}` | Create POI with image upload | Editor |
| `GET` | `/space/pois/{scene_id}` | List all POIs in scene | Viewer |
| `PUT` | `/space/poi/update/{scene_id}/{poi_id}` | Update POI properties | Editor |
| `DELETE` | `/space/poi/delete/{scene_id}/{poi_id}` | Delete POI | Editor |
| `GET` | `/space/scenes/{space_id}` | Get scenes for link POI | Viewer |

## Space & Scene Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/space/view/{space_id}` | View space details |
| `GET` | `/space/scene/{space_id}/{scene_id}` | VR scene viewer |
| `GET` | `/space/edit/{space_id}` | Edit space (Editor only) |
| `POST` | `/space/insert/{space_id}` | Create scene (Editor only) |

---

# Development Roadmap

## ✅ Completed (v0.3.0)

### Phase 0: Security & Performance (v0.2.0)
- ✅ Permission validation fixes
- ✅ MongoDB indexes
- ✅ ObjectId validation with error handling
- ✅ Exception handling (400/401/403/404/500)
- ✅ Password hashing deduplication

### Phase 1-3: POI System (v0.3.0)
- ✅ Backend API (CRUD endpoints)
- ✅ POI data models and validation
- ✅ Database methods (create/get/update/delete)
- ✅ Frontend modal UI
- ✅ A-Frame 3D components
- ✅ VR scene integration
- ✅ Editor keyboard shortcuts
- ✅ Migration scripts

## 📋 Planned

개선 계획 및 개발 전략은 [`.claude/todos/`](.claude/todos/) 폴더를 참고하세요:

- 📋 [ROADMAP.md](.claude/todos/ROADMAP.md) - 전체 개선 로드맵
- ⚡ [priority-2-short-term.md](.claude/todos/priority-2-short-term.md) - N+1 쿼리 해결, API 표준화
- 🏗️ [priority-3-mid-term.md](.claude/todos/priority-3-mid-term.md) - Redis 캐싱, GraphQL
- 🎬 POI 고급 기능 - 애니메이션, 비디오/오디오 POI
- 👥 멀티플레이어 - 실시간 협업 편집

---

# Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with bcrypt
- **Frontend**: Jinja2, Bootstrap
- **VR**: A-Frame (WebVR framework)
- **Storage**: GridFS (MongoDB)
- **3D**: Three.js (via A-Frame)

---

# Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

# License

This project is licensed under the MIT License.

---

# Contact & Support

- GitHub Issues: Report bugs or request features
- Documentation: See `.claude/todos/` for detailed development plans
