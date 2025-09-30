# 테스트 데이터 준비 가이드 🧪

> **목표**: POI 시스템 개발 및 테스트를 위한 샘플 데이터 생성
> **소요 시간**: 1-2시간

---

## 📋 필요한 테스트 데이터

### 1. 360도 이미지 (Space 배경)
- **개수**: 최소 3개
- **형식**: JPG/PNG
- **해상도**: 4096×2048 (2:1 비율) 또는 8192×4096
- **용량**: 각 5-15MB

### 2. POI용 이미지
- **개수**: 10-15개
- **형식**: JPG/PNG/WEBP
- **해상도**: 512×512 (정사각형 권장)
- **용량**: 각 200KB-2MB

### 3. 테스트 사용자 계정
- **개수**: 2개 (Editor, Viewer)
- **역할**: 권한 테스트용

---

## 🖼️ 무료 360도 이미지 소스

### 1. Flickr (Creative Commons)
```bash
# 검색 키워드
- "360 panorama"
- "equirectangular"
- "360 degrees"
- "photosphere"

# 필터: Creative Commons License
```
**링크**: https://www.flickr.com/search/?text=360%20panorama&license=2%2C3%2C4%2C5%2C6%2C9

### 2. Poly Pizza (구글 Poly 아카이브)
**링크**: https://poly.pizza/
- 3D 모델 및 360 이미지
- CC 라이선스

### 3. 직접 촬영 (스마트폰)
**Android**: Google Street View 앱
**iOS**:
- Google Street View 앱
- Panorama 360 앱

**촬영 팁**:
1. 한 자리에서 360도 회전하며 촬영
2. 조명이 균일한 장소 선택
3. 사람이 움직이지 않는 시간대

### 4. AI 생성 (선택)
```bash
# Stable Diffusion + ControlNet
prompt: "modern office interior, 360 degree equirectangular panorama"
# 또는
# Midjourney with --panorama flag
```

---

## 🎨 POI 이미지 소스

### 1. Unsplash (무료 고해상도)
**링크**: https://unsplash.com/
```bash
# 카테고리
- Architecture (건축물)
- Nature (자연)
- Travel (여행지)
- History (역사)
- Art (예술작품)
```

### 2. Pexels
**링크**: https://www.pexels.com/
- 완전 무료
- 상업적 사용 가능

### 3. Pixabay
**링크**: https://pixabay.com/
- 무료 라이선스

---

## 🛠️ 테스트 데이터 생성 스크립트

### 1. MongoDB 시드 데이터 (seed_data.py)
```python
# manage/seed_data.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import sys
sys.path.append('..')

from app.core.libs.utils import get_password_hash

async def seed_database():
    # MongoDB 연결
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["simulverse_test"]  # 테스트 DB

    print("🌱 시드 데이터 생성 시작...")

    # 1. 기존 데이터 삭제 (테스트 DB만!)
    await db.users.delete_many({})
    await db.spaces.delete_many({})
    await db.scenes.delete_many({})
    await db.links.delete_many({})
    print("✅ 기존 데이터 삭제 완료")

    # 2. 테스트 사용자 생성
    users = [
        {
            "_id": ObjectId(),
            "userid": "editor_test",
            "email": "editor@test.com",
            "hashed_password": get_password_hash("test1234"),
            "spaces": {}
        },
        {
            "_id": ObjectId(),
            "userid": "viewer_test",
            "email": "viewer@test.com",
            "hashed_password": get_password_hash("test1234"),
            "spaces": {}
        }
    ]

    result = await db.users.insert_many(users)
    editor_id = users[0]["_id"]
    viewer_id = users[1]["_id"]
    print(f"✅ 사용자 생성 완료: {len(result.inserted_ids)}명")

    # 3. 공간(Space) 생성
    space1 = {
        "_id": ObjectId(),
        "name": "테스트 박물관",
        "explain": "POI 시스템 테스트를 위한 가상 박물관입니다.",
        "creator": editor_id,
        "viewers": {
            str(editor_id): "Editor",
            str(viewer_id): "Viewer"
        },
        "scenes": {}
    }

    space2 = {
        "_id": ObjectId(),
        "name": "현대 오피스",
        "explain": "현대적인 사무실 공간",
        "creator": editor_id,
        "viewers": {
            str(editor_id): "Editor"
        },
        "scenes": {}
    }

    await db.spaces.insert_many([space1, space2])
    print(f"✅ 공간 생성 완료: 2개")

    # 사용자에게 공간 연결
    await db.users.update_one(
        {"_id": editor_id},
        {"$set": {
            "spaces": {
                str(space1["_id"]): "Editor",
                str(space2["_id"]): "Editor"
            }
        }}
    )
    await db.users.update_one(
        {"_id": viewer_id},
        {"$set": {"spaces": {str(space1["_id"]): "Viewer"}}}
    )

    # 4. 씬(Scene) 생성 (이미지는 나중에 업로드)
    scene1 = {
        "_id": ObjectId(),
        "name": "입구 로비",
        "image_id": None,  # TODO: 이미지 업로드 후 설정
        "links": [],
        "pois": [
            # 샘플 POI 데이터
            {
                "poi_id": ObjectId(),
                "type": "info",
                "title": "박물관 안내",
                "description": "이 박물관은 1920년에 설립되었으며, 다양한 역사적 유물을 소장하고 있습니다.",
                "position": {"x": 2.0, "y": 1.5, "z": -3.0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "image_id": None,  # TODO: 이미지 업로드 후 설정
                "visible": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "poi_id": ObjectId(),
                "type": "info",
                "title": "관람 시간",
                "description": "화-일요일: 09:00-18:00\\n월요일: 휴관",
                "position": {"x": -2.0, "y": 1.2, "z": -2.5},
                "rotation": {"x": 0, "y": 45, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "image_id": None,
                "visible": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
    }

    scene2 = {
        "_id": ObjectId(),
        "name": "전시실 1",
        "image_id": None,
        "links": [],
        "pois": [
            {
                "poi_id": ObjectId(),
                "type": "info",
                "title": "고대 유물",
                "description": "기원전 2000년경의 도자기 컬렉션입니다.",
                "position": {"x": 0, "y": 1.8, "z": -4.0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "image_id": None,
                "visible": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
    }

    scene3 = {
        "_id": ObjectId(),
        "name": "전시실 2",
        "image_id": None,
        "links": [],
        "pois": []
    }

    await db.scenes.insert_many([scene1, scene2, scene3])
    print(f"✅ 씬 생성 완료: 3개 (총 3개 POI 포함)")

    # 5. 링크(Link) 생성
    link1 = {
        "_id": ObjectId(),
        "target_id": scene2["_id"],
        "x": 0, "y": 0, "z": -6,
        "yaw": 0, "pitch": 0, "roll": 0
    }

    link2 = {
        "_id": ObjectId(),
        "target_id": scene3["_id"],
        "x": 3, "y": 0, "z": -3,
        "yaw": 45, "pitch": 0, "roll": 0
    }

    link3 = {
        "_id": ObjectId(),
        "target_id": scene1["_id"],  # 다시 로비로
        "x": 0, "y": 0, "z": 6,
        "yaw": 180, "pitch": 0, "roll": 0
    }

    await db.links.insert_many([link1, link2, link3])
    print(f"✅ 링크 생성 완료: 3개")

    # 씬에 링크 연결
    await db.scenes.update_one(
        {"_id": scene1["_id"]},
        {"$set": {"links": [link1["_id"], link2["_id"]]}}
    )
    await db.scenes.update_one(
        {"_id": scene2["_id"]},
        {"$set": {"links": [link3["_id"]]}}
    )

    # 공간에 씬 연결
    await db.spaces.update_one(
        {"_id": space1["_id"]},
        {"$set": {
            "scenes": {
                str(scene1["_id"]): "입구 로비",
                str(scene2["_id"]): "전시실 1",
                str(scene3["_id"]): "전시실 2"
            }
        }}
    )

    print("\\n🎉 시드 데이터 생성 완료!")
    print(f"\\n📊 생성된 데이터:")
    print(f"  - 사용자: 2명")
    print(f"  - 공간: 2개")
    print(f"  - 씬: 3개")
    print(f"  - POI: 3개")
    print(f"  - 링크: 3개")
    print(f"\\n🔑 테스트 계정:")
    print(f"  - Editor: editor@test.com / test1234")
    print(f"  - Viewer: viewer@test.com / test1234")
    print(f"\\n⚠️  이미지 업로드는 웹 UI 또는 image_upload.py 스크립트를 사용하세요")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
```

**실행 방법**:
```bash
cd manage
python seed_data.py
```

---

### 2. 이미지 업로드 스크립트 (image_upload.py)
```python
# manage/image_upload.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import motor.motor_asyncio
from bson import ObjectId
from pathlib import Path
import sys

async def upload_test_images():
    """테스트 이미지를 GridFS에 업로드"""
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["simulverse_test"]

    # GridFS 버킷
    fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db, bucket_name="images")

    print("📤 테스트 이미지 업로드 시작...")

    # 이미지 디렉토리
    image_dir = Path("../test_images")

    if not image_dir.exists():
        print(f"❌ 이미지 디렉토리가 없습니다: {image_dir}")
        print(f"💡 다음 명령으로 디렉토리를 생성하세요:")
        print(f"   mkdir -p test_images/360")
        print(f"   mkdir -p test_images/poi")
        return

    # 360도 이미지 업로드
    scene_images = {}
    for img_path in (image_dir / "360").glob("*.jpg"):
        print(f"  📷 업로드 중: {img_path.name}")
        with open(img_path, 'rb') as f:
            image_id = await fs.upload_from_stream(
                filename=img_path.name,
                source=f,
                metadata={"type": "scene", "content_type": "image/jpeg"}
            )
            scene_images[img_path.stem] = image_id
            print(f"    ✅ ID: {image_id}")

    # POI 이미지 업로드
    poi_images = {}
    for img_path in (image_dir / "poi").glob("*.*"):
        print(f"  🖼️  업로드 중: {img_path.name}")
        content_type = "image/jpeg" if img_path.suffix == ".jpg" else "image/png"
        with open(img_path, 'rb') as f:
            image_id = await fs.upload_from_stream(
                filename=img_path.name,
                source=f,
                metadata={"type": "poi", "content_type": content_type}
            )
            poi_images[img_path.stem] = image_id
            print(f"    ✅ ID: {image_id}")

    print(f"\\n✅ 업로드 완료: 360도 {len(scene_images)}개, POI {len(poi_images)}개")

    # 씬에 이미지 연결 (선택)
    if scene_images:
        print("\\n🔗 씬에 이미지 연결 중...")
        scenes = await db.scenes.find({}).to_list(None)
        image_ids = list(scene_images.values())

        for i, scene in enumerate(scenes):
            if i < len(image_ids):
                await db.scenes.update_one(
                    {"_id": scene["_id"]},
                    {"$set": {"image_id": image_ids[i]}}
                )
                print(f"  ✅ {scene['name']}: {image_ids[i]}")

    # POI에 이미지 연결 (선택)
    if poi_images:
        print("\\n🔗 POI에 이미지 연결 중...")
        scenes_with_pois = await db.scenes.find({"pois": {"$exists": True, "$ne": []}}).to_list(None)
        poi_image_ids = list(poi_images.values())
        img_idx = 0

        for scene in scenes_with_pois:
            for poi in scene.get("pois", []):
                if img_idx < len(poi_image_ids):
                    await db.scenes.update_one(
                        {"_id": scene["_id"], "pois.poi_id": poi["poi_id"]},
                        {"$set": {"pois.$.image_id": poi_image_ids[img_idx]}}
                    )
                    print(f"  ✅ {poi['title']}: {poi_image_ids[img_idx]}")
                    img_idx += 1

    print("\\n🎉 모든 이미지 업로드 및 연결 완료!")
    client.close()

if __name__ == "__main__":
    asyncio.run(upload_test_images())
```

**실행 방법**:
```bash
cd manage
python image_upload.py
```

---

## 📂 이미지 디렉토리 구조

```
simulverse/
├── test_images/              # Git에서 제외 (.gitignore)
│   ├── 360/                  # 360도 이미지
│   │   ├── lobby.jpg         # 로비 (4096×2048)
│   │   ├── room1.jpg         # 전시실 1
│   │   └── room2.jpg         # 전시실 2
│   └── poi/                  # POI 이미지
│       ├── museum_info.jpg   # 박물관 안내 (512×512)
│       ├── opening_hours.jpg # 관람 시간
│       ├── artifacts.jpg     # 유물
│       └── ...
└── manage/
    ├── seed_data.py          # 데이터 생성
    └── image_upload.py       # 이미지 업로드
```

---

## 🚀 빠른 시작 가이드

### Step 1: 이미지 다운로드
```bash
# 테스트 이미지 디렉토리 생성
mkdir -p test_images/360
mkdir -p test_images/poi

# Unsplash에서 이미지 다운로드 (예시)
# 360도 이미지 (equirectangular)
curl -L "https://source.unsplash.com/4096x2048/?museum,interior" -o test_images/360/lobby.jpg
curl -L "https://source.unsplash.com/4096x2048/?gallery,art" -o test_images/360/room1.jpg
curl -L "https://source.unsplash.com/4096x2048/?exhibition,hall" -o test_images/360/room2.jpg

# POI 이미지 (정사각형)
curl -L "https://source.unsplash.com/512x512/?museum,sign" -o test_images/poi/museum_info.jpg
curl -L "https://source.unsplash.com/512x512/?clock,time" -o test_images/poi/opening_hours.jpg
curl -L "https://source.unsplash.com/512x512/?ancient,pottery" -o test_images/poi/artifacts.jpg
```

**주의**: Unsplash API는 매번 다른 이미지를 반환할 수 있습니다. 실제로는 수동으로 다운로드하는 것이 좋습니다.

### Step 2: 데이터 생성
```bash
cd manage
python seed_data.py
```

### Step 3: 이미지 업로드
```bash
python image_upload.py
```

### Step 4: 로그인 및 테스트
```
URL: http://localhost:8000/login
ID: editor@test.com
PW: test1234
```

---

## 🎨 직접 360도 이미지 촬영 가이드

### Android (Google Street View 앱)
1. Google Play에서 "Street View" 설치
2. 앱 실행 → 하단 "만들기" 탭
3. "360° 사진" 선택
4. 화면 안내에 따라 회전하며 촬영
5. 완료 후 "비공개"로 저장
6. 갤러리에서 이미지 추출

### iOS (Panorama 360 앱)
1. App Store에서 "Panorama 360" 설치
2. 카메라 모드 → "360"
3. 한 자리에서 회전하며 촬영
4. 완료 후 카메라롤에 저장

### DSLR/미러리스 (수동)
1. 삼각대 필수
2. 수동 모드 (ISO, 셔터, 조리개 고정)
3. 15-20도 간격으로 촬영 (24-36장)
4. PTGui, Hugin 등으로 스티칭

---

## 📦 샘플 데이터 패키지 (선택)

나중에 팀원들과 공유할 수 있도록 샘플 데이터 패키지를 만들 수 있습니다:

```bash
# 데이터 익스포트
mongodump --db simulverse_test --out backup/

# 압축
tar -czf simulverse_sample_data.tar.gz backup/ test_images/

# 공유 (Google Drive, Dropbox 등)
```

**복원 방법**:
```bash
# 압축 해제
tar -xzf simulverse_sample_data.tar.gz

# 데이터 임포트
mongorestore --db simulverse_test backup/simulverse_test/

# 이미지는 이미 GridFS에 포함됨
```

---

## ✅ 체크리스트

### 준비 단계
- [ ] `test_images/360/` 디렉토리 생성
- [ ] `test_images/poi/` 디렉토리 생성
- [ ] 360도 이미지 3개 다운로드 (4096×2048)
- [ ] POI 이미지 5-10개 다운로드 (512×512)

### 스크립트 작성
- [ ] `manage/seed_data.py` 작성
- [ ] `manage/image_upload.py` 작성
- [ ] `.gitignore`에 `test_images/` 추가

### 실행
- [ ] `python seed_data.py` 실행
- [ ] `python image_upload.py` 실행
- [ ] 로그인 테스트 (editor@test.com)
- [ ] 씬 렌더링 확인
- [ ] POI 표시 확인

### 문서화
- [ ] README에 테스트 데이터 생성 가이드 추가
- [ ] 팀원에게 이미지 소스 공유

---

## 🔒 보안 주의사항

1. **테스트 DB 분리**:
   - 운영 DB: `simulverse`
   - 테스트 DB: `simulverse_test`

2. **이미지 라이선스 확인**:
   - 상업적 사용 가능한지 확인
   - CC0, CC BY 라이선스 권장

3. **테스트 계정 비밀번호**:
   - 개발 환경: `test1234` (간단)
   - 스테이징: 강력한 비밀번호
   - 운영: 절대 테스트 계정 사용 금지

---

**예상 소요 시간**:
- 이미지 수집: 30분
- 스크립트 작성: 30분
- 실행 및 검증: 30분
- **총 1.5시간**

**다음 단계**: [feature-poi-system.md](./feature-poi-system.md) Phase 1 시작
