from fastapi.responses import HTMLResponse
from os.path import dirname, abspath
from pathlib import Path
from fastapi import APIRouter, Depends, Request, responses, HTTPException, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from jose import JWTError, jwt

from ..models.database import db_manager
from ..instance import config
from ..models.auth_manager import auth_manager, get_current_user
from ..schemas.space_model import CreateSpaceForm


router = APIRouter(include_in_schema=False)

db_manager.init_manager(config.MONGODB_URL, "simulverse")
BASE_DIR = dirname(dirname(abspath(__file__)))

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

@router.get("/create/", response_class=HTMLResponse)
async def create(request: Request, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        return templates.TemplateResponse("create/create_space.html", {"request": request, "data": {}, "login":True})

@router.post("/create/", response_class=HTMLResponse)
async def handle_create(request: Request, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        form = CreateSpaceForm(request)
        await form.load_data()
        
        token = request.cookies.get('access_token')
        payload = jwt.decode(token.split()[1], config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM])
        userid: str = payload.get("sub")
        
        if await db_manager.create_space(userid, form):
            response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
        else:
            response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)

        
        return response
        '''if await db_manager.create_user(form):
            return responses.RedirectResponse(
                "/?msg=Successfully-Registered", status_code=status.HTTP_302_FOUND
            )  # default is post request, to use get request added status code 302
        else:
            form.__dict__.get("errors").append("Duplicate username or email")
            return templates.TemplateResponse("manage/register.html", form.__dict__)'''