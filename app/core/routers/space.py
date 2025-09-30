from fastapi.responses import HTMLResponse
from os.path import dirname, abspath
from pathlib import Path
from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from bson.objectid import ObjectId

from ..models.database import db_manager
from ..config import settings
from ..models.auth_manager import get_current_user
from ..schemas.space_model import CreateSceneForm, CreateSpaceForm, UpdateSceneForm
from ..libs.utils import validate_object_id

import json

router = APIRouter(include_in_schema=False)

db_manager.init_manager(settings.MONGODB_URL, settings.MONGODB_DATABASE)
BASE_DIR = dirname(dirname(abspath(__file__)))

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

@router.get("/space/view/{space_id}", response_class=HTMLResponse)
async def space(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space = await db_manager.get_space(validate_object_id(space_id))
        if space:
            user_id = str(auth_user.id)
            # Check if user is in viewers dictionary
            if user_id in space.viewers:
                data = {'text':f"<h1>{space.name}</h1><p/><h3>{space.explain}</h3>",
                        'role':space.viewers[user_id], 'scenes':space.scenes, 'space_id':space.id}

                '''
                data.text = space explain
                data.scenes
                data.space_id
                data.role
                '''
                return templates.TemplateResponse("space/view_space.html", {"request": request, "data": data, "login":True})
            else:
                response = RedirectResponse("/?error=401", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
                return response

@router.get("/space/insert/{space_id}", response_class=HTMLResponse)
async def insert_scene(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)
        # Only Editor can create scenes
        if user_id not in space.viewers or space.viewers[user_id] != 'Editor':
            response = RedirectResponse("/?error=403", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            return response

        scenes = await db_manager.get_scenes_from_space(validate_object_id(space_id))

        data = {"scenes":scenes}
        return templates.TemplateResponse("space/create_scene.html", {"request": request, "data":data, "login":True})

@router.post("/space/insert/{space_id}", response_class=HTMLResponse)
async def handle_insert_scene(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)
        # Only Editor can create scenes
        if user_id not in space.viewers or space.viewers[user_id] != 'Editor':
            response = RedirectResponse("/?error=403", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            return response

        form = CreateSceneForm(request)
        await form.load_data()
        if await form.is_valid():
            await db_manager.create_scene(form, validate_object_id(space_id))

            response = RedirectResponse(f"/space/view/{space_id}", status_code=status.HTTP_302_FOUND)
            return response
        else:
            form.__dict__.update(request=request)
            form.__dict__.update(data={})
            return templates.TemplateResponse(f"space/create_scene.html", form.__dict__)

@router.get("/space/scene/{space_id}/{scene_id}", response_class=HTMLResponse)
async def scene(request: Request, space_id: str, scene_id:str, auth_user= Depends(get_current_user)):
    '''
    Fetch scene data
    :param request:browser's request, scene_id: id of a scene with ObjectID, auth_user: authuentication
    '''
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        scene_oid = validate_object_id(scene_id)
        scene = await db_manager.get_scene(scene_oid)
        links = []
        for link in scene["links"]:
            target_link = await db_manager.get_collection("links").find_one({'_id':link})
            target_name = await db_manager.get_scene(target_link['target_id'])

            links.append([target_name['name'], target_link['target_id']
                                             , target_link['x']
                                             , target_link['y']
                                             , target_link['z']
                                             , target_link['yaw']
                                             , target_link['pitch']
                                             , target_link['roll']
                                             , target_link['_id']])

        # Get POIs for this scene
        pois = await db_manager.get_pois(scene_oid)

        # Convert ObjectIds to strings for template
        for poi in pois:
            if 'poi_id' in poi:
                poi['poi_id'] = str(poi['poi_id'])
            if 'image_id' in poi and poi['image_id']:
                poi['image_id'] = str(poi['image_id'])
            if 'target_scene_id' in poi and poi['target_scene_id']:
                poi['target_scene_id'] = str(poi['target_scene_id'])

        # Check if user has Editor permission
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)
        is_editor = user_id in space.viewers and space.viewers[user_id] == 'Editor'

        data = {
            'space_id': space_id,
            'scene_id': scene_id,
            'background': scene['image_id'],
            'links': links,
            'pois': pois,
            'is_editor': is_editor
        }
        return templates.TemplateResponse("aframe/scene.html", {"request": request, "data": data, "login":True})

@router.get("/space/scene/edit/{space_id}/{scene_id}", response_class=HTMLResponse)
async def scene_edit(request: Request, scene_id:str, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)
        # Only Editor can edit scenes
        if user_id not in space.viewers or space.viewers[user_id] != 'Editor':
            response = RedirectResponse("/?error=403", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            return response

        '''
        {'_id': ObjectId('632f2186b763ee36b2407771'), 'target_id':ObjectId('632f21a1b763ee36b2407785'), 'x':'0', 'y':'1', 'z':'-6'}
        '''

        scene = await db_manager.get_scene(validate_object_id(scene_id))

        scenes = await db_manager.get_scenes_from_space(validate_object_id(space_id))

        link_info = []
        for l in scene["links"]:
            link = await db_manager.get_link(l)
            link_info.append(link)

        data = {'name': scene['name'], 'image_id':scene['image_id'], "scenes":scenes, "links":link_info}
        return templates.TemplateResponse("space/update_scene.html", {"request": request, "data": data, "login":True})

@router.post("/space/scene/edit/{space_id}/{scene_id}", response_class=HTMLResponse)
async def handle_scene_edit(request: Request, scene_id:str, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)
        # Only Editor can edit scenes
        if user_id not in space.viewers or space.viewers[user_id] != 'Editor':
            response = RedirectResponse("/?error=403", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            return response

        form = UpdateSceneForm(request)
        await form.load_data()

        if await form.is_valid():
            await db_manager.update_scene(form, space_id=validate_object_id(space_id), scene_id=validate_object_id(scene_id))

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
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)
        # Check if user exists in viewers AND has Editor role
        if user_id in space.viewers and space.viewers[user_id] == 'Editor':
            viewers = {}
            for user, val in space.viewers.items():
                #print(user, val)
                _user = await db_manager.get_user_by_id(validate_object_id(user))
                if auth_user.email != _user.email:
                    viewers[_user.email] = val

            #print(viewers)
            data = {'space_name':space.name, 'space_explain':space.explain, 'invite_lists':viewers}
            return templates.TemplateResponse("space/update_space.html", {"request": request, "data": data, "login":True})
        else:
            # Unauthorized - redirect to home with error
            response = RedirectResponse("/?error=403", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            return response

@router.post("/space/edit/{space_id}", response_class=HTMLResponse)
async def handle_update_space(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)
        # Only Editor can update space
        if user_id not in space.viewers or space.viewers[user_id] != 'Editor':
            response = RedirectResponse("/?error=403", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            return response

        form = CreateSpaceForm(request)
        await form.load_data()

        response = None
        if await form.is_valid():
            await db_manager.update_space(auth_user, validate_object_id(space_id), form)
            response = RedirectResponse(f"/view/", status_code=status.HTTP_302_FOUND)
        else:
            response = RedirectResponse(f"/view/?error=c01", status_code=status.HTTP_302_FOUND)
        return response

@router.post("/space/delete/scene/{space_id}/{scene_id}", response_class=HTMLResponse)
async def handle_delete_scene(request: Request, space_id:str, scene_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)
        # Only Editor can delete scenes
        if user_id not in space.viewers or space.viewers[user_id] != 'Editor':
            response = RedirectResponse("/?error=403", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            return response

        # delete scene
        await db_manager.delete_scene(validate_object_id(space_id), validate_object_id(scene_id))

        response = RedirectResponse(f"/view/", status_code=status.HTTP_302_FOUND)
        return response

@router.post("/space/delete/space/{space_id}")
async def handle_delete_space(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        space_oid = validate_object_id(space_id)
        space = await db_manager.get_space(space_oid)
        user_id = str(auth_user.id)
        # Only Editor can delete space
        if user_id not in space.viewers or space.viewers[user_id] != 'Editor':
            response = RedirectResponse("/?error=403", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            return response

        # delete scene
        result = await db_manager.get_collection('spaces').find_one({'_id':space_oid})
        for scene in result['scenes']:
            await db_manager.delete_scene(space_oid, ObjectId(scene))

        await db_manager.get_collection('spaces').delete_one({'_id':space_oid})
        await db_manager.get_collection('users').update_many({}, {'$unset':{f"spaces.{str(space_id)}":""}})

        response = RedirectResponse(f"/", status_code=status.HTTP_302_FOUND)
        return response

@router.put("/space/scene/link/update/{space_id}")
async def handle_link_update(request: Request, space_id:str, auth_user= Depends(get_current_user)):
    if not auth_user :
        response = RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return response
    else:
        # check ownership
        space = await db_manager.get_space(validate_object_id(space_id))
        user_id = str(auth_user.id)

        # Verify user has Editor role
        if user_id in space.viewers and space.viewers[user_id] == 'Editor':
            _body = await request.body()
            _body = result = json.loads(_body.decode('utf-8'))
            for key, val in _body.items():
                data = {'x':val[0]["x"], 'y':val[0]["y"], 'z':val[0]["z"], 'yaw':val[1]["x"], 'pitch':val[1]["y"], "roll":val[1]["z"]}
                link = await db_manager.get_collection('links').update_one({'_id':validate_object_id(key)}, {'$set':data})

            return 'done'
        else:
            return 'Not authorized'
       