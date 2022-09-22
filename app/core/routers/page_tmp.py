from fastapi.responses import HTMLResponse
from os.path import dirname, abspath
from pathlib import Path
from fastapi import APIRouter, Depends, Request, responses, HTTPException, status
from fastapi.templating import Jinja2Templates
from jose import jwt

from ..models.database import db_manager
from ..instance import config
from ..models.auth_manager import auth_manager, get_current_user
from ..schemas.space_model import CreateSpaceForm
from ..libs.resolve_error import resolve_error

router = APIRouter(include_in_schema=False)

db_manager.init_manager(config.MONGODB_URL, "simulverse")
BASE_DIR = dirname(dirname(abspath(__file__)))

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    data = {'text': '<h1>Welcome to the Simulverse Management System </h1>\n'}  
    return templates.TemplateResponse("page.html", {"request": request, "data": data, "login": False})
    '''if not auth_user :
        
    else:
        spaces = await db_manager.get_spaces(auth_user)
        data = {'text':'<h1>Welcome to the Simulverse Management System </h1>', 'spaces':spaces} 
        
        errors = []
        if 'error' in request.query_params:
            errors = [ resolve_error(x) for x in request.query_params['error'].split('.')]
        
        return templates.TemplateResponse("page.html", {"request": request, "data": data, "login": True, "errors":errors})'''

@router.get("/scene/{scene_id}", response_class=HTMLResponse)
async def get_scene(request: Request, scene_id: int):
    data = {'text': f'<h1>Welcome to the Simulverse Management System </h1>\n<p>#TODO: Scene{scene_id}.</p>'}  
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

@router.get("/view/", response_class=HTMLResponse)
async def view(request: Request, auth_user= Depends(get_current_user)):
    if not auth_user :
        data = {'text': '<h1>Welcome to the Simulverse Management System </h1>\n<p>Please Log-in or Sign-up.</p>'}  
        return templates.TemplateResponse("page.html", {"request": request, "data": data, "login": False})
    else:
        spaces = await db_manager.get_spaces(auth_user)
        data = {'text':'<h1>Welcome to the Simulverse Management System </h1>', 'spaces':spaces} 
        
        errors = []
        if 'error' in request.query_params:
            errors = [ resolve_error(x) for x in request.query_params['error'].split('.')]
        
        return templates.TemplateResponse("page.html", {"request": request, "data": data, "login": True, "errors":errors})

@router.get("/vr/", response_class=HTMLResponse)
async def vr(request: Request, auth_user= Depends(get_current_user)):
    
    data = {'text': f'<h1>Welcome to the Simulverse Management System </h1>\n<p>#TODO: View.</p>'}  
    return templates.TemplateResponse("aframe/scene.html", {"request": request, "data": data})
        
#@router.get("/login/", response_class=HTMLResponse)
#async def login(request: Request):
#    data = {'text': f'<h1>Welcome to the Simulverse Management System </h1>\n<p>#TODO: authentication.</p>'}  
#    return templates.TemplateResponse("page.html", {"request": request, "data": data})
