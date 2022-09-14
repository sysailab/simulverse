import motor.motor_asyncio
from ..schemas.user_model import UserRegisterForm, UserInDB
from ..libs.utils import verify_password
from ..libs.utils import get_password_hash

from fastapi.encoders import jsonable_encoder

class db_manager(object):
    client = None
    db = None

    @classmethod
    def init_manager(cls, _url, _dbname):
        cls.client = motor.motor_asyncio.AsyncIOMotorClient(_url)
        cls.db = cls.client[_dbname]

    @classmethod
    def get_collection(cls, name):
        return cls.db[name]

    @classmethod
    async def get_user(cls, email: str) -> UserInDB|None:
        document = await cls.get_collection("users").find_one({'email': email})
        if document:
            return UserInDB(**document)
        else:
            return None

    @classmethod
    async def authenticate_user(cls, userid: str, password: str):
        user = await cls.get_user(userid)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    @classmethod
    async def create_user(cls, user:UserRegisterForm):
        userdata = await cls.get_user(user.username)
        if userdata:
            return False
        else:
            data = UserInDB()
            data.userid = user.username
            data.email = user.email
            data.is_active = False
            data.hashed_password = get_password_hash(user.password)
            document = jsonable_encoder(data)
            await db_manager.get_collection('users').insert_one(document) 
            return True
