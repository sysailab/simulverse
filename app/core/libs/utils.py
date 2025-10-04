import bcrypt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from bson.objectid import ObjectId
from bson.errors import InvalidId

#from app.instance import config
from typing import Any


class _BcryptAbout:
    """Shim to provide version metadata expected by passlib."""

    def __init__(self):
        version = getattr(bcrypt, "__version__", "0")
        self.__version__ = version


# bcrypt 5.0.0 misses __about__, passlib relies on it for backend detection
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = _BcryptAbout()
if hasattr(bcrypt, "_bcrypt") and not hasattr(bcrypt._bcrypt, "__about__"):
    bcrypt._bcrypt.__about__ = bcrypt.__about__

if hasattr(bcrypt, "_bcrypt"):
    _raw_hashpw = bcrypt._bcrypt.hashpw
    _raw_checkpw = bcrypt._bcrypt.checkpw

    def _truncate_secret(secret: bytes | str) -> bytes:
        data = secret.encode("utf-8") if isinstance(secret, str) else secret
        if len(data) > 72:
            return data[:72]
        return data

    def _patched_hashpw(secret, config):
        return _raw_hashpw(_truncate_secret(secret), config)

    def _patched_checkpw(secret, hashed):
        return _raw_checkpw(_truncate_secret(secret), hashed)

    bcrypt._bcrypt.hashpw = _patched_hashpw
    bcrypt.hashpw = _patched_hashpw
    bcrypt._bcrypt.checkpw = _patched_checkpw
    bcrypt.checkpw = _patched_checkpw


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """Compare plain password with stored hash, tolerating bcrypt limits."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        # bcrypt refuses passwords longer than 72 bytes – treat as auth failure
        return False

def get_password_hash(password):
    return pwd_context.hash(password)


def validate_object_id(id_value: Any) -> ObjectId:
    """Convert a value into ObjectId or raise a 400 HTTPException."""
    if isinstance(id_value, ObjectId):
        return id_value
    try:
        return ObjectId(str(id_value))
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail="Invalid ID format")
