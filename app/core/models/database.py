import motor.motor_asyncio

from bson.objectid import ObjectId
from fastapi import Request

from ..libs.utils import verify_password
from ..libs.utils import get_password_hash

from ..schemas.user_model import UserRegisterForm, UserInDB
from ..schemas.space_model import CreateSpaceForm, SpaceModel, CreateSceneForm, UpdateSceneForm


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
    async def get_user_by_email(cls, email: str) -> UserInDB|None:
        document = await cls.get_collection("users").find_one({'email': email})
        if document:
            return UserInDB(**document)
        else:
            return None
    
    @classmethod
    async def get_user_by_id(cls, userid:ObjectId) -> UserInDB|None:
        document = await cls.get_collection("users").find_one({'_id': userid})
        if document:
            return UserInDB(**document)
        else:
            return None

    @classmethod
    async def authenticate_user(cls, userid: str, password: str):
        user = await cls.get_user_by_email(userid)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    @classmethod
    async def create_user(cls, user:UserRegisterForm):
        userdata = await cls.get_user_by_email(user.email)
        if userdata:
            return False
        else:
            data = {'userid':user.username, 'email':user.email, 'spaces':{}, 'hashed_password':get_password_hash(user.password)}
            await db_manager.get_collection('users').insert_one(data) 
            return True

    @classmethod
    async def create_space(cls, creator: str, space:CreateSpaceForm):
        userdata = await cls.get_user_by_email(creator)
        viewers = {str(userdata.id):'Editor'}
        for _id, role in zip(space.form_data['username'], space.form_data['role']):
            view = await cls.get_user_by_email(_id)
            if view :
                viewers[str(view.id)] = role

        data = {'name':space.form_data['space_name'][0], 'explain': space.form_data['space_explain'][0], 
                'creator': userdata.id, 'viewers':viewers, 'scenes':{}}
        space_id = await db_manager.get_collection('spaces').insert_one(data) 

        for viewer, val in viewers.items():
            await db_manager.get_collection('users').update_one({'_id':ObjectId(viewer)}, [{"$set": {'spaces': {str(space_id.inserted_id): val}}}]) 

    @classmethod
    async def update_space(cls, creator: UserInDB, space_id:ObjectId, space:CreateSpaceForm):
        viewers = {str(creator.id):'Editor'}
        for _id, role in zip(space.form_data['username'], space.form_data['role']):
            view = await cls.get_user_by_email(_id)
            if view :
                viewers[str(view.id)] = role
        print("viewers", viewers)
        
        print('deletion')
        found_space = await db_manager.get_collection('spaces').find_one({'_id':space_id})
        for viewer, val in found_space['viewers'].items():
            if viewer not in viewers:
                print(viewer, val)
                await db_manager.get_collection('users').update_one({'_id':ObjectId(viewer)}, {"$unset": {f'spaces.{str(space_id)}': ""}}) 
            else:
                await db_manager.get_collection('users').update_one({'_id':ObjectId(viewer)}, [{"$set": {'spaces': {str(space_id): val}}}])

        print('deletion')

        data = {'name':space.form_data['space_name'][0], 'explain': space.form_data['space_explain'][0], 'viewers':viewers}
        print('space update', data)
        await db_manager.get_collection('spaces').update_one({'_id':space_id}, {"$unset": {f'viewers': ""}})
        await db_manager.get_collection('spaces').update_one({'_id':space_id}, [{'$set':data}]) 
    
    @classmethod
    async def create_scene(cls, form:CreateSceneForm, space_id:ObjectId ):
        image_id = await cls.store_image(form.form_data['file'][0].filename, 
                                        form.form_data['file'][0].content_type, 
                                        form.form_data['file'][0].file )
        '''
        link: link_name, scene_id, x, y, z
        '''
        links = []
        if 'scene' in form.form_data:
            links = list(zip(form.scene[1:], form.x[1:],form.y[1:], form.z[1:]))
        data = {'name':form.scene_name, 'image_id':image_id, 'links':links}
        scene_id = await db_manager.get_collection('scenes').insert_one(data)
        await db_manager.get_collection('spaces').update_one({'_id':ObjectId(space_id)}, [{"$set": {'scenes': {str(scene_id.inserted_id): form.scene_name}}}]) 

    @classmethod
    async def update_scene(cls, form:UpdateSceneForm, space_id:ObjectId, scene_id:ObjectId ):
        '''
        link: link_name, scene_id, x, y, z
        '''
        links = []
        if 'scene' in form.form_data:
            links = list(zip(form.scene, form.x,form.y, form.z))

        data = {'name':form.scene_name, 'links':links}
        print(data)
        await db_manager.get_collection('scenes').update_one({'_id':scene_id},{"$unset": {f'links': []}})
        await db_manager.get_collection('scenes').update_one({'_id':scene_id},[{"$set": data}])
        await db_manager.get_collection('spaces').update_one({'_id':space_id}, [{"$set": {'scenes': {str(scene_id): form.scene_name}}}]) 

    @classmethod
    async def get_scene(cls, scene_id:ObjectId ):
        scene = await db_manager.get_collection('scenes').find_one({"_id":scene_id})
        return scene

    @classmethod
    async def get_scenes_from_space(cls, spaceid: ObjectId):
        scenes = []
        cursor = await cls.get_collection("spaces").find_one({"_id":spaceid})
        for sceneid, scene_name in cursor["scenes"].items():
            scenes.append((sceneid, scene_name))
        
        return scenes

    @classmethod
    async def get_spaces(cls, creator: UserInDB):
        spaces = []
        for spaceid, role in creator.spaces.items():
            cursor = await cls.get_collection("spaces").find_one({"_id":ObjectId(spaceid)})
            spaces.append((cursor["name"], cursor['explain'], spaceid, role))

        return spaces

    @classmethod
    async def get_space(cls, space_id: ObjectId):
        cursor = await cls.get_collection("spaces").find_one({"_id":space_id})
        return SpaceModel(**cursor)

    @classmethod
    async def store_image(cls, filename:str, metadata, contents):
        fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(cls.db, bucket_name="images")
        return await fs.upload_from_stream(filename=filename, source=contents, metadata=metadata)

    @classmethod
    async def download_file(cls, file_id):
        """Returns iterator over AsyncIOMotorGridOut object"""
        fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(cls.db, bucket_name="images")
        gridout = await fs.open_download_stream(file_id)
        content = await gridout.read()

        return (content, gridout.content_type)
        