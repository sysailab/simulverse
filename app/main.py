import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from os.path import dirname, abspath
from pathlib import Path
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.models.database import db_manager
from .core.models.auth_manager import auth_manager
from .core.schemas.token_model import Token
from .core.config import settings

from app.core.routers import page_view, register, login, create, space, asset

BASE_DIR = dirname(abspath(__file__))
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'core/templates')))

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(Path(BASE_DIR, 'static'))), name="static")
db_manager.init_manager(settings.MONGODB_URL, settings.MONGODB_DATABASE)

app.include_router(register.router, prefix="", tags=["register"])
app.include_router(page_view.router, prefix="", tags=["home"])
app.include_router(login.router, prefix="", tags=["login"])
app.include_router(create.router, prefix="", tags=["create"])
app.include_router(space.router, prefix="", tags=["space"])
app.include_router(asset.router, prefix="", tags=["asset"])

logger = logging.getLogger("simulverse.main")

ERROR_PAGE_CONTENT = {
    status.HTTP_403_FORBIDDEN: ("접근이 거부되었습니다", "요청하신 리소스에 접근할 수 없습니다."),
    status.HTTP_404_NOT_FOUND: ("페이지를 찾을 수 없습니다", "요청하신 리소스를 찾지 못했습니다."),
    status.HTTP_500_INTERNAL_SERVER_ERROR: ("서버 오류", "예기치 못한 오류가 발생했습니다."),
}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await auth_manager.create_access_token(
        data={"sub": user.userid}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse("/login/?error=unauthorized", status_code=status.HTTP_302_FOUND)

    title, default_message = ERROR_PAGE_CONTENT.get(
        exc.status_code, ("오류가 발생했습니다", "요청을 처리할 수 없습니다.")
    )
    message = exc.detail if exc.detail else default_message
    context = {
        "request": request,
        "login": False,
        "data": {"code": exc.status_code, "title": title, "message": message},
    }
    return templates.TemplateResponse("error.html", context, status_code=exc.status_code)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled application error", exc_info=exc)
    title, message = ERROR_PAGE_CONTENT[status.HTTP_500_INTERNAL_SERVER_ERROR]
    context = {
        "request": request,
        "login": False,
        "data": {
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "title": title,
            "message": message,
        },
    }
    return templates.TemplateResponse(
        "error.html", context, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

