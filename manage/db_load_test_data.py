from instance import config
import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def do_insert(db, data:dict):
    for k, v in data.items():
        for item in v:
            document = jsonable_encoder(item)
            result = await db[k].insert_one(document)

client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGODB_URL)
db = client["simulverse"]
data = {'users':[{'userid':'rhchoi', 'email':'rhchoi@example.com','is_active':False, 'hashed_password':f'{get_password_hash("123123")}'}]}
loop = client.get_io_loop()
loop.run_until_complete(do_insert(db, data))
