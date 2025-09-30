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

from .core.models.database import db_manager
from .core.models.auth_manager import auth_manager
from .core.schemas.token_model import Token
from .core.config import settings

from app.core.routers import page_view, register, login, create, space, asset, poi

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
app.include_router(poi.router, prefix="", tags=["poi"])

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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with appropriate responses based on status code."""

    # 400 Bad Request - Invalid input
    if exc.status_code == 400:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": 400,
                "message": "잘못된 요청입니다.",
                "detail": exc.detail or "입력값을 확인해주세요."
            },
            status_code=400
        )

    # 401 Unauthorized - Not authenticated
    elif exc.status_code == 401:
        return RedirectResponse("/login/?error=unauthorized", status_code=status.HTTP_302_FOUND)

    # 403 Forbidden - Not authorized
    elif exc.status_code == 403:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": 403,
                "message": "접근 권한이 없습니다.",
                "detail": "이 작업을 수행할 권한이 없습니다."
            },
            status_code=403
        )

    # 404 Not Found
    elif exc.status_code == 404:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": 404,
                "message": "페이지를 찾을 수 없습니다.",
                "detail": "요청하신 리소스가 존재하지 않습니다."
            },
            status_code=404
        )

    # 500 Internal Server Error
    elif exc.status_code == 500:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Internal server error: {exc.detail}")

        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": 500,
                "message": "서버 오류가 발생했습니다.",
                "detail": "잠시 후 다시 시도해주세요."
            },
            status_code=500
        )

    # Default - other status codes
    else:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": exc.status_code,
                "message": f"오류가 발생했습니다 ({exc.status_code})",
                "detail": exc.detail or "알 수 없는 오류입니다."
            },
            status_code=exc.status_code
        )