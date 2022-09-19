from fastapi.responses import HTMLResponse
from os.path import dirname, abspath
from pathlib import Path
from fastapi import APIRouter, Depends, Request, responses, HTTPException, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from bson.objectid import ObjectId

from ..models.database import db_manager
from ..instance import config
from ..models.auth_manager import get_current_user
from ..schemas.space_model import CreateSceneForm, SpaceModel


router = APIRouter(include_in_schema=False)

db_manager.init_manager(config.MONGODB_URL, "simulverse")
BASE_DIR = dirname(dirname(abspath(__file__)))

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

@router.get("/space/view/{space_id}", response_class=HTMLResponse)
async def space(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        print(space_id)
        space = await db_manager.get_space(ObjectId(space_id))
        if str(auth_user.id) in space.viewers:
            data = {'text':f"<h1>{space.name}</h1><p/><h3>{space.explain}</h3>",
                    'role':space.viewers[str(auth_user.id)], 'scenes':space.scenes, 'space_id':space.id}
            print(data)
            '''
            data.text = space explain
            data.scenes
            data.space_id
            data.role
            '''
            return templates.TemplateResponse("space/view_space.html", {"request": request, "data": data, "login":True})
        else:
            response = RedirectResponse("/?error=401", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/space/insert/{space_id}", response_class=HTMLResponse)        
async def insert_scene(request: Request, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        return templates.TemplateResponse("create/create_scene.html", {"request": request})

@router.post("/space/insert/{space_id}", response_class=HTMLResponse)        
async def handle_insert_scene(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        form = CreateSceneForm(request)
        await form.load_data()
        await db_manager.create_scene(form, ObjectId(space_id))

        response = RedirectResponse(f"/space/view/{space_id}", status_code=status.HTTP_302_FOUND)
        return response


@router.get("/space/edit/{space_id}", response_class=HTMLResponse)
async def space(request: Request, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        return templates.TemplateResponse("create/create_space.html", {"request": request, "data": {}, "login":True})

@router.get("/space/edit/{space_id}", response_class=HTMLResponse)
async def space(request: Request, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        return templates.TemplateResponse("create/create_space.html", {"request": request, "data": {}, "login":True})
