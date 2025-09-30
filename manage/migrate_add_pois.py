#!/usr/bin/env python3
"""
MongoDB Migration Script - Add POIs field to scenes

This script adds a 'pois' array field to all existing scenes in the database.
Run this script once before deploying the POI system.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient


async def migrate():
    """Add pois field to all scenes that don't have it"""

    # MongoDB connection
    print("🔌 MongoDB 연결 중...")
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["simulverse"]

    print("🔄 마이그레이션 시작...\n")

    try:
        # Count scenes without pois field
        scenes_without_pois = await db.scenes.count_documents({"pois": {"$exists": False}})

        if scenes_without_pois == 0:
            print("✅ 모든 씬에 이미 'pois' 필드가 있습니다. 마이그레이션이 필요하지 않습니다.")
            return

        print(f"📊 'pois' 필드가 없는 씬: {scenes_without_pois}개\n")

        # Add pois field to scenes without it
        result = await db.scenes.update_many(
            {"pois": {"$exists": False}},
            {"$set": {"pois": []}}
        )

        print(f"✅ 마이그레이션 완료!")
        print(f"   - 수정된 씬: {result.modified_count}개")

        # Verify migration
        total_scenes = await db.scenes.count_documents({})
        scenes_with_pois = await db.scenes.count_documents({"pois": {"$exists": True}})

        print(f"\n📊 마이그레이션 결과:")
        print(f"   - 전체 씬: {total_scenes}개")
        print(f"   - pois 필드가 있는 씬: {scenes_with_pois}개")

        if total_scenes == scenes_with_pois:
            print("\n✅ 모든 씬이 성공적으로 마이그레이션되었습니다!")
        else:
            print(f"\n⚠️  경고: {total_scenes - scenes_with_pois}개의 씬이 마이그레이션되지 않았습니다.")

    except Exception as e:
        print(f"\n❌ 마이그레이션 오류: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except KeyboardInterrupt:
        print("\n\n❌ 작업 취소됨")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
