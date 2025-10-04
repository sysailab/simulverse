#!/usr/bin/env python3
"""
데이터베이스 전체 삭제 스크립트
⚠️ 주의: 이 스크립트는 데이터베이스의 모든 데이터를 삭제합니다!
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def drop_database():
    """데이터베이스 삭제"""

    print("="*60)
    print("  ⚠️  데이터베이스 삭제 경고")
    print("="*60)
    print()
    print("이 작업은 다음 데이터를 영구적으로 삭제합니다:")
    print("  - 모든 사용자 계정")
    print("  - 모든 공간(Space)과 씬(Scene)")
    print("  - 모든 POI 데이터")
    print("  - 모든 링크")
    print("  - GridFS에 저장된 모든 이미지")
    print()
    print("⚠️  이 작업은 되돌릴 수 없습니다!")
    print()

    # 데이터베이스 선택
    default_db = settings.MONGODB_DATABASE
    test_db = f"{default_db}_test"

    print("삭제할 데이터베이스를 선택하세요:")
    print(f"  1. {default_db} (운영 DB) ⚠️ ")
    print(f"  2. {test_db} (테스트 DB)")
    print("  3. 취소")
    print()

    choice = input("선택 (1/2/3): ").strip()

    if choice == "3" or not choice:
        print("\n✅ 작업 취소됨")
        return

    if choice == "1":
        db_name = default_db
    elif choice == "2":
        db_name = test_db
    else:
        print("\n❌ 잘못된 선택. 작업 취소됨")
        return

    # 최종 확인
    print()
    print(f"🔴 정말로 '{db_name}' 데이터베이스를 삭제하시겠습니까?")
    confirm = input(f"'{db_name}'를 입력하여 확인: ").strip()

    if confirm != db_name:
        print("\n❌ 확인 실패. 작업 취소됨")
        return

    # MongoDB 연결
    print(f"\n🔌 MongoDB 연결 중...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[db_name]

    print(f"🗑️  '{db_name}' 데이터베이스 삭제 중...")

    try:
        # 컬렉션별 데이터 개수 확인
        print("\n📊 삭제 전 데이터 현황:")
        collections = await db.list_collection_names()
        total_docs = 0

        for coll_name in collections:
            if not coll_name.startswith("system."):
                count = await db[coll_name].count_documents({})
                total_docs += count
                print(f"  - {coll_name}: {count}개")

        if collections:
            print(f"\n총 {len(collections)}개 컬렉션, {total_docs}개 문서")
        else:
            print("  (비어있음)")

        # GridFS 파일 개수
        fs_files_count = await db["images.files"].count_documents({}) if "images.files" in collections else 0
        if fs_files_count > 0:
            print(f"  - GridFS 이미지: {fs_files_count}개")

        print()

        # 데이터베이스 삭제 실행
        await client.drop_database(db_name)

        print("="*60)
        print("✅ 데이터베이스 삭제 완료!")
        print("="*60)
        print(f"\n'{db_name}' 데이터베이스가 완전히 삭제되었습니다.")
        print()
        print("💡 새로운 데이터를 생성하려면:")
        print(f"   python db_setup.py")
        print()

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    try:
        asyncio.run(drop_database())
    except KeyboardInterrupt:
        print("\n\n❌ 작업 취소됨")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
