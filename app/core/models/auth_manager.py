import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jwt import PyJWTError, encode, decode
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .database import db_manager
from ..schemas.user_model import UserModel, UserInDB
from ..schemas.token_model import Token, TokenData
from ..libs.utils import verify_password
from ..libs.oauth2_cookie import OAuth2PasswordBearerWithCookie
from ..config import settings

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/token", auto_error=False)

class auth_manager(object):
    @classmethod
    async def authenticate_user(cls, userid: str, password: str):
        user = await db_manager.get_user_by_email(userid)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
    
    @classmethod
    async def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if not token:
            return None
        payload = decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

        userid: str = payload.get("sub")
        if userid is None:
            raise credentials_exception
        token_data = TokenData(email=userid)
    except PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    user = await db_manager.get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    return {"current_user":"user"}