import os
from datetime import datetime, timedelta
#from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from .database import db_manager
from ..schemas.user_model import UserModel, UserInDB
from ..schemas.token_model import Token, TokenData
from ..libs.utils import verify_password
from ..libs.oauth2_cookie import OAuth2PasswordBearerWithCookie
from ..instance import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/token")

class auth_manager(object):
    @classmethod
    async def authenticate_user(cls, userid: str, password: str):
        user = await db_manager.get_user(userid)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
    
    @classmethod
    async def create_access_token(cls, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.ALGORITHM)
        return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM])
        userid: str = payload.get("sub")
        print(userid)
        if userid is None:
            raise credentials_exception
        token_data = TokenData(email=userid)
    except JWTError:
        raise credentials_exception
    user = await db_manager.get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user