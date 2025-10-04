#!/usr/bin/env python3
"""Create the MongoDB indexes required by Simulverse."""

import asyncio
import sys
from pathlib import Path

from pymongo.errors import OperationFailure
from motor.motor_asyncio import AsyncIOMotorClient

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings

INDEX_DEFINITIONS = {
    "users": (("email", {"unique": True}),),
    "spaces": (("creator", {}), ("viewers", {})),
    "scenes": (("image_id", {}),),
    "links": (("target_id", {}),),
}


async def ensure_indexes(db):
    """Ensure the required indexes exist on the given database."""
    for collection_name, index_specs in INDEX_DEFINITIONS.items():
        collection = db[collection_name]
        for field, options in index_specs:
            kwargs = dict(options)
            try:
                index_name = await collection.create_index(field, **kwargs)
                print(f"✅ {collection_name}.{field} -> {index_name}")
            except OperationFailure as exc:
                print(f"⚠️ Failed to create {collection_name}.{field}: {exc}")


async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    try:
        await ensure_indexes(db)
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())

