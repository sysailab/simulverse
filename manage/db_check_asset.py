import asyncio
import pprint
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import motor.motor_asyncio
from app.core.config import settings

async def do_check(db, collections:list):
    for item in collections:
        cursor = db[item].find({})
        for document in await cursor.to_list(length=100):
            print(type(document["_id"]))
            pprint.pprint(document)

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

loop = client.get_io_loop()
loop.run_until_complete(do_check(db, ['images']))
