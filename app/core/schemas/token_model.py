from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: Optional[str] = None


class TokenData(BaseModel):
    email: str = ""