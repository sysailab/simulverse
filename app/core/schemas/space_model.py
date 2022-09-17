from fastapi import Request
from pydantic import BaseModel

class CreateSpaceForm: 
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: list = []
        self.username: str = ""
        self.email: str = ""
        self.password: str = ""

    async def load_data(self):
        form = await self.request.form()
        contents = form.multi_items()
        self.form_data = {}
        for k, v in contents:
            if k not in self.form_data:
                self.form_data.setdefault(k, []).append(v)
            else:
                self.form_data[k].append(v)