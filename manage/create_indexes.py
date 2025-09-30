#!/usr/bin/env python3
"""
MongoDB Index Creation Script

This script creates indexes for the Simulverse database to improve query performance.
Run this script after initial database setup or when deploying to production.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient


async def create_indexes():
    """Create all necessary indexes for the database collections."""

    # MongoDB connection
    print("🔌 MongoDB 연결 중...")
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["simulverse"]

    print("Creating indexes...")

    try:
        # Users collection indexes
        print("- Creating users indexes...")
        await db.users.create_index("email", unique=True, name="email_unique_idx")
        print("  ✓ email (unique)")

        # Spaces collection indexes
        print("- Creating spaces indexes...")
        await db.spaces.create_index("creator", name="spaces_creator_idx")
        print("  ✓ creator")
        await db.spaces.create_index("viewers", name="spaces_viewers_idx")
        print("  ✓ viewers")

        # Scenes collection indexes
        print("- Creating scenes indexes...")
        await db.scenes.create_index("image_id", name="scenes_image_id_idx")
        print("  ✓ image_id")

        # Links collection indexes
        print("- Creating links indexes...")
        await db.links.create_index("target_id", name="links_target_id_idx")
        print("  ✓ target_id")

        print("\n✅ All indexes created successfully!")

        # List all indexes
        print("\n📊 Index Summary:")
        print("\nUsers collection:")
        for idx in await db.users.list_indexes().to_list(length=100):
            print(f"  - {idx['name']}: {idx.get('key', {})}")

        print("\nSpaces collection:")
        for idx in await db.spaces.list_indexes().to_list(length=100):
            print(f"  - {idx['name']}: {idx.get('key', {})}")

        print("\nScenes collection:")
        for idx in await db.scenes.list_indexes().to_list(length=100):
            print(f"  - {idx['name']}: {idx.get('key', {})}")

        print("\nLinks collection:")
        for idx in await db.links.list_indexes().to_list(length=100):
            print(f"  - {idx['name']}: {idx.get('key', {})}")

    except Exception as e:
        print(f"\n❌ Error creating indexes: {e}")
        raise
    finally:
        # Close database connection
        client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())
