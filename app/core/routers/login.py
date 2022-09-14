from os.path import dirname, abspath
from pathlib import Path
from datetime import timedelta

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse

from ..models.database import db_manager
from ..models.auth_manager import auth_manager
from ..instance.config import MONGODB_URL, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas.user_model import UserLoginForm, UserModel

router = APIRouter(include_in_schema=False)

db_manager.init_manager(MONGODB_URL, "simulverse")
BASE_DIR = dirname(dirname(abspath(__file__)))

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

@router.get("/login/")
def render_login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login/")
async def handle_login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_manager.authenticate_user(form_data.username, form_data.password)
    if user :
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await auth_manager.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        form_data.__dict__.update(msg="Login Successful :)")
        form_data.__dict__.update(request=request)
        form_data.__dict__.update(data={})
        response = templates.TemplateResponse("page.html", form_data.__dict__)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response

    else:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return templates.TemplateResponse("auth/login.html", {"request": request})

    '''
    @app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get(form_data.username, None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
    }
    '''