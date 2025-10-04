from fastapi.responses import HTMLResponse
from os.path import dirname, abspath
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from ..models.database import db_manager
from ..config import settings
from ..models.auth_manager import get_current_user
from ..schemas.space_model import CreateSceneForm, CreateSpaceForm, UpdateSceneForm
from ..schemas.poi_model import CreatePOIForm
from ..libs.utils import validate_object_id

router = APIRouter(include_in_schema=False)

db_manager.init_manager(settings.MONGODB_URL, settings.MONGODB_DATABASE)
BASE_DIR = dirname(dirname(abspath(__file__)))

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))


def _resolve_viewers(space) -> dict:
    viewers = getattr(space, "viewers", None) or {}
    if isinstance(viewers, dict):
        return viewers
    return dict(viewers)


def _ensure_space(space):
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    return space


def _ensure_member(space, user_id: str) -> str:
    role = _resolve_viewers(space).get(user_id)
    if role is None:
        raise HTTPException(status_code=403, detail="Not authorized for this space")
    return role


def _ensure_editor(space, user_id: str) -> str:
    role = _ensure_member(space, user_id)
    if role != "Editor":
        raise HTTPException(status_code=403, detail="Editor access required")
    return role


async def _render_scene_edit(
    request: Request,
    auth_user,
    space,
    space_oid,
    scene_oid,
    *,
    errors: list[str] | None = None,
    poi_form: dict | None = None,
):
    scene_doc = await db_manager.get_scene(scene_oid)
    if not scene_doc:
        raise HTTPException(status_code=404, detail="Scene not found")

    scenes = await db_manager.get_scenes_from_space(space_oid)

    link_info = []
    for link_id in scene_doc.get("links", []):
        link = await db_manager.get_link(link_id)
        if link:
            link_info.append(link)

    data = {
        'name': scene_doc.get('name'),
        'image_id': scene_doc.get('image_id'),
        'scenes': scenes,
        'links': link_info,
        'pois': scene_doc.get('pois', []),
        'space_id': str(space_oid),
        'scene_id': str(scene_oid),
    }

    context = {
        "request": request,
        "data": data,
        "login": True,
        "errors": errors or [],
        "poi_form": poi_form or {},
    }
    return templates.TemplateResponse("space/update_scene.html", context)


@router.get("/space/view/{space_id}", response_class=HTMLResponse)
async def space(request: Request, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))

    user_id = str(auth_user.id)
    role = _ensure_member(space, user_id)

    data = {
        'text': f"<h1>{space.name}</h1><p/><h3>{space.explain}</h3>",
        'role': role,
        'scenes': space.scenes,
        'space_id': space.id,
    }
    return templates.TemplateResponse("space/view_space.html", {"request": request, "data": data, "login": True})


@router.get("/space/insert/{space_id}", response_class=HTMLResponse)
async def insert_scene(request: Request, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    scenes = await db_manager.get_scenes_from_space(space_oid)
    data = {"scenes": scenes}
    return templates.TemplateResponse("space/create_scene.html", {"request": request, "data": data, "login": True})


@router.post("/space/insert/{space_id}", response_class=HTMLResponse)
async def handle_insert_scene(request: Request, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    form = CreateSceneForm(request)
    await form.load_data()
    if await form.is_valid():
        await db_manager.create_scene(form, space_oid)
        return RedirectResponse(f"/space/view/{space_id}", status_code=status.HTTP_302_FOUND)

    form.__dict__.update(request=request)
    form.__dict__.update(data={})
    return templates.TemplateResponse("space/create_scene.html", form.__dict__)


@router.get("/space/scene/{space_id}/{scene_id}", response_class=HTMLResponse)
async def scene(request: Request, space_id: str, scene_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_member(space, str(auth_user.id))

    scene_oid = validate_object_id(scene_id)
    scene_doc = await db_manager.get_scene(scene_oid)
    if not scene_doc:
        raise HTTPException(status_code=404, detail="Scene not found")

    links = []
    for link_id in scene_doc.get("links", []):
        link = await db_manager.get_collection("links").find_one({'_id': link_id})
        if not link:
            continue
        target_scene = await db_manager.get_scene(link.get('target_id'))
        target_name = target_scene['name'] if target_scene else None
        links.append([
            target_name,
            link.get('target_id'),
            link.get('x'),
            link.get('y'),
            link.get('z'),
            link.get('yaw'),
            link.get('pitch'),
            link.get('roll'),
            link.get('_id'),
        ])

    data = {
        'space_id': space_id,
        'scene_id': scene_id,
        'background': scene_doc.get('image_id'),
        'links': links,
        'pois': scene_doc.get('pois', []),
    }
    return templates.TemplateResponse("aframe/scene.html", {"request": request, "data": data, "login": True})


@router.get("/space/scene/edit/{space_id}/{scene_id}", response_class=HTMLResponse)
async def scene_edit(request: Request, scene_id: str, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    scene_oid = validate_object_id(scene_id)
    return await _render_scene_edit(request, auth_user, space, space_oid, scene_oid)


@router.post("/space/scene/edit/{space_id}/{scene_id}", response_class=HTMLResponse)
async def handle_scene_edit(request: Request, scene_id: str, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    scene_oid = validate_object_id(scene_id)

    form = UpdateSceneForm(request)
    await form.load_data()

    if await form.is_valid():
        await db_manager.update_scene(form, space_id=space_oid, scene_id=scene_oid)
        return RedirectResponse(f"/space/view/{space_id}", status_code=status.HTTP_302_FOUND)

    return await _render_scene_edit(
        request,
        auth_user,
        space,
        space_oid,
        scene_oid,
        errors=form.errors,
    )


@router.post("/space/scene/{space_id}/{scene_id}/poi", response_class=HTMLResponse, name="space_add_poi")
async def create_scene_poi(request: Request, space_id: str, scene_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    scene_oid = validate_object_id(scene_id)

    form = CreatePOIForm(request)
    await form.load_data()
    if await form.is_valid():
        await db_manager.add_scene_poi(scene_oid, form.to_document())
        return RedirectResponse(
            f"/space/scene/edit/{space_id}/{scene_id}", status_code=status.HTTP_302_FOUND
        )

    return await _render_scene_edit(
        request,
        auth_user,
        space,
        space_oid,
        scene_oid,
        errors=form.errors,
        poi_form=form.as_dict(),
    )


@router.post(
    "/space/scene/{space_id}/{scene_id}/poi/{poi_id}/delete",
    response_class=HTMLResponse,
    name="space_delete_poi",
)
async def delete_scene_poi(
    request: Request,
    space_id: str,
    scene_id: str,
    poi_id: str,
    auth_user=Depends(get_current_user),
):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    scene_oid = validate_object_id(scene_id)
    poi_oid = validate_object_id(poi_id)

    await db_manager.remove_scene_poi(scene_oid, poi_oid)

    return RedirectResponse(
        f"/space/scene/edit/{space_id}/{scene_id}", status_code=status.HTTP_302_FOUND
    )





@router.get("/space/edit/{space_id}", response_class=HTMLResponse)
async def edit_space(request: Request, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    viewers = {}
    for user_id, val in _resolve_viewers(space).items():
        user = await db_manager.get_user_by_id(validate_object_id(user_id))
        if user and auth_user.email != user.email:
            viewers[user.email] = val

    data = {'space_name': space.name, 'space_explain': space.explain, 'invite_lists': viewers}
    return templates.TemplateResponse("space/update_space.html", {"request": request, "data": data, "login": True})


@router.post("/space/edit/{space_id}", response_class=HTMLResponse)
async def handle_update_space(request: Request, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    form = CreateSpaceForm(request)
    await form.load_data()

    if await form.is_valid():
        await db_manager.update_space(auth_user, space_oid, form)
        return RedirectResponse("/view/", status_code=status.HTTP_302_FOUND)

    return RedirectResponse("/view/?error=c01", status_code=status.HTTP_302_FOUND)


@router.post("/space/delete/scene/{space_id}/{scene_id}", response_class=HTMLResponse)
async def handle_delete_scene(request: Request, space_id: str, scene_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    scene_oid = validate_object_id(scene_id)
    await db_manager.delete_scene(space_oid, scene_oid)

    return RedirectResponse("/view/", status_code=status.HTTP_302_FOUND)


@router.post("/space/delete/space/{space_id}")
async def handle_delete_space(request: Request, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    for scene_id in (space.scenes or {}):
        await db_manager.delete_scene(space_oid, validate_object_id(scene_id))

    await db_manager.get_collection('spaces').delete_one({'_id': space_oid})
    await db_manager.get_collection('users').update_many({}, {'$unset': {f"spaces.{str(space_oid)}": ""}})

    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@router.put("/space/scene/link/update/{space_id}")
async def handle_link_update(request: Request, space_id: str, auth_user=Depends(get_current_user)):
    if not auth_user:
        return RedirectResponse("/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    space_oid = validate_object_id(space_id)
    space = _ensure_space(await db_manager.get_space(space_oid))
    _ensure_editor(space, str(auth_user.id))

    payload = await request.json()
    for link_id, val in payload.items():
        data = {
            'x': val[0]["x"],
            'y': val[0]["y"],
            'z': val[0]["z"],
            'yaw': val[1]["x"],
            'pitch': val[1]["y"],
            'roll': val[1]["z"],
        }
        await db_manager.get_collection('links').update_one({'_id': validate_object_id(link_id)}, {'$set': data})

    return 'done'

