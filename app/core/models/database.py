import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder

from bson.objectid import ObjectId
from ..libs.pyobjectid import PyObjectId
from ..libs.utils import verify_password
from ..libs.utils import get_password_hash

from ..schemas.user_model import UserRegisterForm, UserInDB
from ..schemas.space_model import CreateSpaceForm, SpaceModel


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
            data = {'userid':user.username, 'email':user.email, 'spaces':{}, 'hashed_password':get_password_hash(user.password)}
            await db_manager.get_collection('users').insert_one(data) 
            return True

    @classmethod
    async def create_space(cls, creator: str, space:CreateSpaceForm):
        userdata = await cls.get_user(creator)
        viewers = {str(userdata.id):'Editor'}
        for _id, role in zip(space.form_data['username'], space.form_data['role']):
            view = await cls.get_user(_id)
            if view :
                viewers[str(view.id)] = role

        data = {'name':space.form_data['space_name'][0], 'explain': space.form_data['space_explain'][0], 'creator': userdata.id, 'viewers':viewers}
        space_id = await db_manager.get_collection('spaces').insert_one(data) 

        for viewer, val in viewers.items():
            result = await db_manager.get_collection('users').update_one({'_id':ObjectId(viewer)}, [{"$set": {'spaces': {str(space_id.inserted_id): val}}}]) 
            print(result.modified_count, result.upserted_id)
        
        userdata = await cls.get_user(creator)
        print(userdata)
        pass
        '''
        name: str = ""
        explain: str = ""
        creator: str = ""
        viewers: dict | None = None
        data = SpaceModel()
        data.name = space.form_data['space_name']
        data.explain = space.form_data['space_explain']
        data.email = user.email
        data.spaces = {}
        data.hashed_password = get_password_hash(user.password)
        document = jsonable_encoder(data)
        await db_manager.get_collection('users').insert_one(document) 



        userdata = await cls.get_user(user.username)
        if userdata:
            return False
        else:
            data = UserInDB()
            data.userid = user.username
            data.email = user.email
            data.spaces = {}
            data.hashed_password = get_password_hash(user.password)
            document = jsonable_encoder(data)
            await db_manager.get_collection('users').insert_one(document) 
            return True
        '''