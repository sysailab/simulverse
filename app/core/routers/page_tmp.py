from fastapi.responses import HTMLResponse
from os.path import dirname, abspath
from pathlib import Path
from fastapi import APIRouter, Depends, Request, responses, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from ..models.database import db_manager
from ..instance.config import MONGODB_URL, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(include_in_schema=False)

db_manager.init_manager(MONGODB_URL, "simulverse")
BASE_DIR = dirname(dirname(abspath(__file__)))

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    data = {'jaiyun': {'abc':'abcd', 'abc1':'abcd', 'abc2':'abcd'}, 'seyoung': {'abc':'abcd', 'abc1':'abcd', 'abc2':'abcd'}}  
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

@router.get("/scene/{scene_id}", response_class=HTMLResponse)
async def get_scene(request: Request, scene_id: int):
    data = {'text': f'<h1>Welcome to the Simulverse Management System </h1>\n<p>#TODO: Scene{scene_id}.</p>'}  
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

@router.get("/manage/", response_class=HTMLResponse)
async def scene_manage(request: Request):
    data = {'text': f'<h1>Welcome to the Simulverse Management System </h1>\n<p>#TODO: SceneManage.</p>'}  
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

@router.get("/view/", response_class=HTMLResponse)
async def view(request: Request):
    data = {'text': f'<h1>Welcome to the Simulverse Management System </h1>\n<p>#TODO: View.</p>'}  
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

@router.get("/create/", response_class=HTMLResponse)
async def create(request: Request):
    data = {'text': f'<h1>Welcome to the Simulverse Management System </h1>\n<p>#TODO: View.</p>'}  
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

#@router.get("/login/", response_class=HTMLResponse)
#async def login(request: Request):
#    data = {'text': f'<h1>Welcome to the Simulverse Management System </h1>\n<p>#TODO: authentication.</p>'}  
#    return templates.TemplateResponse("page.html", {"request": request, "data": data})
