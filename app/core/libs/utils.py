from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

#from app.instance import config
from typing import Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def validate_object_id(id_str: str) -> ObjectId:
    """
    Validate and convert string to ObjectId.

    Args:
        id_str: String representation of ObjectId

    Returns:
        ObjectId: Validated ObjectId

    Raises:
        HTTPException: 400 Bad Request if ID format is invalid
    """
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid ID format")

