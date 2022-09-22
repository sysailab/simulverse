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
from ..schemas.space_model import CreateSceneForm, CreateSpaceForm, UpdateSceneForm



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
        space = await db_manager.get_space(ObjectId(space_id))
        if str(auth_user.id) in space.viewers:
            data = {'text':f"<h1>{space.name}</h1><p/><h3>{space.explain}</h3>",
                    'role':space.viewers[str(auth_user.id)], 'scenes':space.scenes, 'space_id':space.id}
            
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
async def insert_scene(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        scenes = await db_manager.get_scenes_from_space(ObjectId(space_id))
        
        data = {"scenes":scenes}
        return templates.TemplateResponse("space/create_scene.html", {"request": request, "data":data})

@router.post("/space/insert/{space_id}", response_class=HTMLResponse)        
async def handle_insert_scene(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        form = CreateSceneForm(request)
        await form.load_data()
        if form.is_valid():
            await db_manager.create_scene(form, ObjectId(space_id))

            response = RedirectResponse(f"/space/view/{space_id}", status_code=status.HTTP_302_FOUND)
            return response
        else:
            return templates.TemplateResponse(f"/space/insert/{space_id}", form.__dict__)

@router.get("/space/scene/{scene_id}", response_class=HTMLResponse)
async def scene(request: Request, scene_id:str, auth_user= Depends(get_current_user)):
    '''
    Fetch scene data
    :param request:browser's request, scene_id: id of a scene with ObjectID, auth_user: authuentication
    '''
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        scene = await db_manager.get_scene(ObjectId(scene_id))
        print(scene)
        data = {'background':scene['image_id']}
        return templates.TemplateResponse("aframe/scene.html", {"request": request, "data": data, "login":True})

@router.get("/space/scene/edit/{space_id}/{scene_id}", response_class=HTMLResponse)
async def scene_edit(request: Request, scene_id:str, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        scene = await db_manager.get_scene(ObjectId(scene_id))
        scenes = await db_manager.get_scenes_from_space(ObjectId(space_id))
        
        data = {'name': scene['name'], 'image_id':scene['image_id'], "scenes":scenes, "links":scene['links']}
        print(data)
        return templates.TemplateResponse("space/update_scene.html", {"request": request, "data": data, "login":True})

@router.post("/space/scene/edit/{space_id}/{scene_id}", response_class=HTMLResponse)
async def handle_scene_edit(request: Request, scene_id:str, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        form = UpdateSceneForm(request)
        await form.load_data()
        
        if await form.is_valid():
            await db_manager.update_scene(form, ObjectId(space_id), ObjectId(scene_id))

            response = RedirectResponse(f"/space/view/{space_id}", status_code=status.HTTP_302_FOUND)
            return response
        else:
            return templates.TemplateResponse(f"/space/scene/edit/{space_id}/{scene_id}", form.__dict__)

@router.get("/space/edit/{space_id}", response_class=HTMLResponse)
async def edit_space(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space = await db_manager.get_space(ObjectId(space_id))
        if space.viewers[str(auth_user.id)] == 'Editor' and str(auth_user.id) in space.viewers:
            viewers = {}
            for user, val in space.viewers.items():
                _user = await db_manager.get_user_by_id(ObjectId(user))
                if auth_user.email != _user.email:
                    viewers[_user.email] = val

            data = {'space_name':space.name, 'space_explain':space.explain, 'invite_lists':viewers}
            return templates.TemplateResponse("space/update_space.html", {"request": request, "data": data, "login":True})
        else:
            # raise Exception
           return templates.TemplateResponse("space/create_space.html", {"request": request, "data": {}, "login":True})

@router.post("/space/edit/{space_id}", response_class=HTMLResponse)
async def handle_update_space(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        form = CreateSpaceForm(request)
        await form.load_data()

        await db_manager.update_space(auth_user, ObjectId(space_id), form)
        
        return templates.TemplateResponse("space/create_space.html", {"request": request, "data": {}, "login":True})
