#!/usr/bin/env python3
"""
테스트 데이터 시드 스크립트
POI 시스템 개발 및 테스트를 위한 샘플 데이터 생성
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from motor.motor_asyncio import AsyncIOMotorClient
import motor.motor_asyncio
from bson import ObjectId
from datetime import datetime

# 로컬 유틸리티
try:
    from create_indexes import ensure_indexes
except ImportError:
    from manage.create_indexes import ensure_indexes

# app 모듈 import
from app.core.libs.utils import get_password_hash
from app.core.config import settings


async def seed_database():
    """테스트 데이터베이스에 시드 데이터 생성"""

    # MongoDB 연결
    print("🔌 MongoDB 연결 중...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]  # 실제 DB 사용 (주의!)

    # 또는 테스트 DB 사용
    # db = client[f"{settings.MONGODB_DATABASE}_test"]

    print("🧱 인덱스 생성 확인 중...")
    await ensure_indexes(db)

    print("🌱 시드 데이터 생성 시작...\n")

    # ============================================
    # 1. 기존 테스트 데이터 확인
    # ============================================
    existing_users = await db.users.count_documents({"email": {"$regex": "test.com$"}})
    if existing_users > 0:
        print(f"⚠️  경고: 테스트 사용자가 {existing_users}명 이미 존재합니다.")
        response = input("기존 테스트 데이터를 삭제하시겠습니까? (y/N): ")
        if response.lower() == 'y':
            await db.users.delete_many({"email": {"$regex": "test.com$"}})
            print("✅ 기존 테스트 사용자 삭제 완료")
        else:
            print("❌ 작업 취소")
            client.close()
            return

    # ============================================
    # 2. 테스트 사용자 생성
    # ============================================
    print("\n👥 테스트 사용자 생성 중...")

    editor_id = ObjectId()
    viewer_id = ObjectId()

    users = [
        {
            "_id": editor_id,
            "userid": "editor_test",
            "email": "editor@test.com",
            "hashed_password": get_password_hash("test1234"),
            "spaces": {}
        },
        {
            "_id": viewer_id,
            "userid": "viewer_test",
            "email": "viewer@test.com",
            "hashed_password": get_password_hash("test1234"),
            "spaces": {}
        }
    ]

    await db.users.insert_many(users)
    print(f"✅ 사용자 생성 완료: {len(users)}명")
    print(f"   - Editor: editor@test.com / test1234")
    print(f"   - Viewer: viewer@test.com / test1234")

    # ============================================
    # 3. 360도 이미지 업로드 (GridFS)
    # ============================================
    print("\n📤 360도 이미지 업로드 중...")

    fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db, bucket_name="images")
    assets_dir = Path(__file__).parent / "assets"

    image_ids = {}
    for img_path in sorted(assets_dir.glob("space_*.jpg")):
        print(f"  📷 업로드: {img_path.name}")
        with open(img_path, 'rb') as f:
            image_id = await fs.upload_from_stream(
                filename=img_path.name,
                source=f,
                metadata={"type": "scene_360", "content_type": "image/jpeg"}
            )
            image_ids[img_path.stem] = image_id
            print(f"     ✅ ID: {image_id}")

    print(f"✅ 이미지 업로드 완료: {len(image_ids)}개")

    # ============================================
    # 4. 공간(Space) 생성
    # ============================================
    print("\n🏛️  공간 생성 중...")

    space1_id = ObjectId()
    space1 = {
        "_id": space1_id,
        "name": "테스트 박물관",
        "explain": "POI 시스템 테스트를 위한 가상 박물관입니다. 360도 VR로 탐험하세요!",
        "creator": editor_id,
        "viewers": {
            str(editor_id): "Editor",
            str(viewer_id): "Viewer"
        },
        "scenes": {}
    }

    space2_id = ObjectId()
    space2 = {
        "_id": space2_id,
        "name": "현대 갤러리",
        "explain": "현대 미술 작품을 전시하는 갤러리 공간",
        "creator": editor_id,
        "viewers": {
            str(editor_id): "Editor"
        },
        "scenes": {}
    }

    await db.spaces.insert_many([space1, space2])
    print(f"✅ 공간 생성 완료: 2개")

    # ============================================
    # 5. 씬(Scene) 생성 (POI 포함)
    # ============================================
    print("\n🎬 씬 생성 중...")

    image_list = list(image_ids.values())

    # 씬 1: 입구 로비
    scene1_id = ObjectId()
    scene1 = {
        "_id": scene1_id,
        "name": "입구 로비",
        "image_id": image_list[0] if len(image_list) > 0 else None,
        "links": [],
        "pois": [
            {
                "poi_id": ObjectId(),
                "type": "info",
                "title": "박물관 안내",
                "description": "이 박물관은 1920년에 설립되었으며, 다양한 역사적 유물을 소장하고 있습니다. 총 3개의 전시실과 교육 공간으로 구성되어 있습니다.",
                "position": {"x": 2.0, "y": 1.5, "z": -3.0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "image_id": None,
                "visible": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "poi_id": ObjectId(),
                "type": "info",
                "title": "관람 시간",
                "description": "화요일-일요일: 09:00-18:00\n월요일: 휴관\n입장료: 성인 5,000원, 학생 3,000원",
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

    # 씬 2: 전시실 1
    scene2_id = ObjectId()
    scene2 = {
        "_id": scene2_id,
        "name": "전시실 1 - 고대 유물",
        "image_id": image_list[1] if len(image_list) > 1 else None,
        "links": [],
        "pois": [
            {
                "poi_id": ObjectId(),
                "type": "info",
                "title": "고대 도자기 컬렉션",
                "description": "기원전 2000년경의 도자기 컬렉션입니다. 청동기 시대의 생활 양식을 엿볼 수 있습니다.",
                "position": {"x": 0, "y": 1.8, "z": -4.0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "image_id": None,
                "visible": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "poi_id": ObjectId(),
                "type": "info",
                "title": "전시 해설",
                "description": "매일 오전 11시, 오후 2시, 오후 4시에 도슨트 해설이 진행됩니다.",
                "position": {"x": 3.0, "y": 1.5, "z": -2.0},
                "rotation": {"x": 0, "y": -30, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "image_id": None,
                "visible": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
    }

    # 씬 3: 전시실 2
    scene3_id = ObjectId()
    scene3 = {
        "_id": scene3_id,
        "name": "전시실 2 - 근대 미술",
        "image_id": image_list[2] if len(image_list) > 2 else None,
        "links": [],
        "pois": [
            {
                "poi_id": ObjectId(),
                "type": "info",
                "title": "인상파 회화",
                "description": "19세기 후반 프랑스 인상파 화가들의 작품을 감상할 수 있습니다.",
                "position": {"x": -1.5, "y": 1.6, "z": -3.5},
                "rotation": {"x": 0, "y": 20, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "image_id": None,
                "visible": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
    }

    # 씬 4: 특별 전시실
    scene4_id = ObjectId()
    scene4 = {
        "_id": scene4_id,
        "name": "특별 전시실",
        "image_id": image_list[3] if len(image_list) > 3 else None,
        "links": [],
        "pois": []
    }

    await db.scenes.insert_many([scene1, scene2, scene3, scene4])
    total_pois = len(scene1["pois"]) + len(scene2["pois"]) + len(scene3["pois"])
    print(f"✅ 씬 생성 완료: 4개 (총 {total_pois}개 POI 포함)")

    # ============================================
    # 6. 링크(Link) 생성 - 씬 간 이동
    # ============================================
    print("\n🔗 링크 생성 중...")

    # 로비 → 전시실 1
    link1_id = ObjectId()
    link1 = {
        "_id": link1_id,
        "target_id": scene2_id,
        "x": 0, "y": 0, "z": -6,
        "yaw": 0, "pitch": 0, "roll": 0
    }

    # 로비 → 전시실 2
    link2_id = ObjectId()
    link2 = {
        "_id": link2_id,
        "target_id": scene3_id,
        "x": 3, "y": 0, "z": -3,
        "yaw": 45, "pitch": 0, "roll": 0
    }

    # 전시실 1 → 로비
    link3_id = ObjectId()
    link3 = {
        "_id": link3_id,
        "target_id": scene1_id,
        "x": 0, "y": 0, "z": 6,
        "yaw": 180, "pitch": 0, "roll": 0
    }

    # 전시실 1 → 특별 전시실
    link4_id = ObjectId()
    link4 = {
        "_id": link4_id,
        "target_id": scene4_id,
        "x": -3, "y": 0, "z": -3,
        "yaw": -45, "pitch": 0, "roll": 0
    }

    # 전시실 2 → 로비
    link5_id = ObjectId()
    link5 = {
        "_id": link5_id,
        "target_id": scene1_id,
        "x": -3, "y": 0, "z": 3,
        "yaw": 135, "pitch": 0, "roll": 0
    }

    await db.links.insert_many([link1, link2, link3, link4, link5])
    print(f"✅ 링크 생성 완료: 5개")

    # 씬에 링크 연결
    await db.scenes.update_one(
        {"_id": scene1_id},
        {"$set": {"links": [link1_id, link2_id]}}
    )
    await db.scenes.update_one(
        {"_id": scene2_id},
        {"$set": {"links": [link3_id, link4_id]}}
    )
    await db.scenes.update_one(
        {"_id": scene3_id},
        {"$set": {"links": [link5_id]}}
    )

    # ============================================
    # 7. 공간에 씬 연결
    # ============================================
    print("\n🔗 공간-씬 연결 중...")

    await db.spaces.update_one(
        {"_id": space1_id},
        {"$set": {
            "scenes": {
                str(scene1_id): "입구 로비",
                str(scene2_id): "전시실 1 - 고대 유물",
                str(scene3_id): "전시실 2 - 근대 미술",
                str(scene4_id): "특별 전시실"
            }
        }}
    )
    print("✅ 공간-씬 연결 완료")

    # ============================================
    # 8. 사용자에게 공간 할당
    # ============================================
    print("\n🔗 사용자-공간 연결 중...")

    await db.users.update_one(
        {"_id": editor_id},
        {"$set": {
            "spaces": {
                str(space1_id): "Editor",
                str(space2_id): "Editor"
            }
        }}
    )
    await db.users.update_one(
        {"_id": viewer_id},
        {"$set": {
            "spaces": {
                str(space1_id): "Viewer"
            }
        }}
    )
    print("✅ 사용자-공간 연결 완료")

    # ============================================
    # 9. 완료 요약
    # ============================================
    print("\n" + "="*50)
    print("🎉 시드 데이터 생성 완료!")
    print("="*50)
    print(f"\n📊 생성된 데이터:")
    print(f"  👥 사용자: 2명")
    print(f"  🏛️  공간: 2개")
    print(f"  🎬 씬: 4개")
    print(f"  📍 POI: {total_pois}개")
    print(f"  🔗 링크: 5개")
    print(f"  🖼️  360도 이미지: {len(image_ids)}개")

    print(f"\n🔑 테스트 계정:")
    print(f"  📧 Editor: editor@test.com")
    print(f"  🔒 Password: test1234")
    print(f"  📧 Viewer: viewer@test.com")
    print(f"  🔒 Password: test1234")

    print(f"\n🚀 다음 단계:")
    print(f"  1. 서버 실행: python simulverse.py http")
    print(f"  2. 브라우저: http://localhost:8000/login")
    print(f"  3. 로그인 후 '테스트 박물관' 공간 확인")
    print(f"  4. POI 시스템 개발 시작!")

    print("\n" + "="*50)

    client.close()


if __name__ == "__main__":
    try:
        asyncio.run(seed_database())
    except KeyboardInterrupt:
        print("\n\n❌ 작업 취소됨")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
