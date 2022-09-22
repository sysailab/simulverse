from fastapi import Request
from pydantic import BaseModel, Field
from bson import ObjectId

from ..libs.pyobjectid import PyObjectId

class SpaceModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = ""
    explain: str = ""
    creator: PyObjectId = Field(default_factory=PyObjectId)
    viewers: dict | None = None
    scenes: dict | None = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    pass
    
class CreateSpaceForm: 
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: list = []
        self.form_data = {}

    async def load_data(self):
        form = await self.request.form()
        contents = form.multi_items()
        
        for k, v in contents:
            if k not in self.form_data:
                self.form_data.setdefault(k, []).append(v)
            else:
                self.form_data[k].append(v)


class CreateSceneForm: 
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: list = []
        self.form_data = {}

    async def load_data(self):
        form = await self.request.form()
        contents = form.multi_items()
        
        for k, v in contents:
            print(k,v)
            if k not in self.form_data:
                self.form_data.setdefault(k, []).append(v)
            else:
                self.form_data[k].append(v)

        for key, val in self.form_data.items():
            if len(val) > 1:
                setattr(self, key, val[1:])
            else:
                setattr(self, key, val[0])

    async def is_valid(self):
        if not self.name:
            self.errors.append("Name is required")
        if not self.image_id:
            self.errors.append("Image File is required")
        if not self.errors:
            return True
        return False

class UpdateSceneForm: 
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: list = []
        self.form_data = {}

    async def load_data(self):
        form = await self.request.form()
        contents = form.multi_items()
        
        for k, v in contents:
            if k not in self.form_data:
                self.form_data.setdefault(k, []).append(v)
            else:
                self.form_data[k].append(v)

        for key, val in self.form_data.items():
            print(key, val)
            if len(val) > 1:
                setattr(self, key, val[1:])
            else:
                setattr(self, key, val[0])

    async def is_valid(self):
        if not self.scene_name:
            self.errors.append("Name is required")
        if not self.errors:
            return True
        return False