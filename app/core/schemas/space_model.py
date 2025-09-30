from fastapi import Request
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from typing import Dict, Any, Optional

class SpaceModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    name: str = ""
    explain: str = ""
    creator: ObjectId = Field(default_factory=ObjectId)
    viewers: Optional[Dict[str, Any]] = None
    scenes: Optional[Dict[str, Any]] = None
    
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

    async def is_valid(self):
        if not self.form_data['space_name'][0]:
            self.errors.append("Space name is required")
        if not self.form_data['space_explain'][0]:
            self.errors.append("Space explanation is required")
        if not self.errors:
            return True
        return False
class CreateSceneForm:
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
            if len(val) > 1:
                setattr(self, key, val)
            else:
                setattr(self, key, val[0])

        if hasattr(self, 'scene') and len(self.scene) > 1:
            self.scene = self.scene[1:]
        if hasattr(self, 'x') and len(self.x) > 1:
            self.x = self.x[1:]
        if hasattr(self, 'y') and len(self.y) > 1:
            self.y = self.y[1:]
        if hasattr(self, 'z') and len(self.z) > 1:
            self.z = self.z[1:]
        if hasattr(self, 'yaw') and len(self.yaw) > 1:
            self.yaw = self.yaw[1:]
        if hasattr(self, 'pitch') and len(self.pitch) > 1:
            self.pitch = self.pitch[1:]
        if hasattr(self, 'roll') and len(self.roll) > 1:
            self.roll = self.roll[1:]

    async def is_valid(self):
        if not hasattr(self, 'scene_name') or not self.scene_name:
            self.errors.append("Name is required")
        if not hasattr(self, 'file') or not self.file:
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
            if len(val) > 1:
                setattr(self, key, val)
            else:
                setattr(self, key, val[0])

        if hasattr(self, 'scene') and len(self.scene) > 1:
            self.scene = self.scene[1:]
        if hasattr(self, 'x') and len(self.x) > 1:
            self.x = self.x[1:]
        if hasattr(self, 'y') and len(self.y) > 1:
            self.y = self.y[1:]
        if hasattr(self, 'z') and len(self.z) > 1:
            self.z = self.z[1:]
        if hasattr(self, 'yaw') and len(self.yaw) > 1:
            self.yaw = self.yaw[1:]
        if hasattr(self, 'pitch') and len(self.pitch) > 1:
            self.pitch = self.pitch[1:]
        if hasattr(self, 'roll') and len(self.roll) > 1:
            self.roll = self.roll[1:]

    async def is_valid(self):
        if not hasattr(self, 'scene_name') or not self.scene_name:
            self.errors.append("Name is required")
        if not self.errors:
            return True
        return False