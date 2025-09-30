"""
POI Router

API endpoints for managing Points of Interest (POIs) in scenes.
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from typing import Optional, Literal
import motor.motor_asyncio

from ..models.database import db_manager
from ..config import settings
from ..models.auth_manager import get_current_user
from ..libs.utils import validate_object_id
from ..schemas.poi_model import CreatePOIForm, UpdatePOIForm, POIResponse

router = APIRouter(include_in_schema=False)

db_manager.init_manager(settings.MONGODB_URL, settings.MONGODB_DATABASE)


async def check_editor_permission(space_id: ObjectId, user_id: str) -> bool:
    """Check if user has Editor permission for the space."""
    space = await db_manager.get_space(space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    return user_id in space.viewers and space.viewers[user_id] == 'Editor'


@router.post("/space/poi/create/{scene_id}")
async def create_poi(
    request: Request,
    scene_id: str,
    poi_type: Literal["info", "link", "media"] = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    x: float = Form(...),
    y: float = Form(...),
    z: float = Form(...),
    rotation_x: float = Form(0),
    rotation_y: float = Form(0),
    rotation_z: float = Form(0),
    scale_x: float = Form(1),
    scale_y: float = Form(1),
    scale_z: float = Form(1),
    visible: bool = Form(True),
    target_scene_id: Optional[str] = Form(None),
    media_url: Optional[str] = Form(None),
    media_type: Optional[Literal["video", "audio"]] = Form(None),
    image: Optional[UploadFile] = File(None),
    auth_user=Depends(get_current_user)
):
    """
    Create a new POI in a scene.
    Only users with Editor permission can create POIs.
    """
    if not auth_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    scene_oid = validate_object_id(scene_id)

    # Get space_id from scene
    scene = await db_manager.get_scene(scene_oid)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    # Find space that contains this scene
    space = await db_manager.get_collection('spaces').find_one(
        {f"scenes.{scene_id}": {"$exists": True}}
    )
    if not space:
        raise HTTPException(status_code=404, detail="Space not found for scene")

    # Check Editor permission
    user_id = str(auth_user.id)
    if not await check_editor_permission(space['_id'], user_id):
        raise HTTPException(status_code=403, detail="Editor permission required")

    # Handle image upload if provided
    image_id = None
    if image and poi_type == "info":
        # Upload to GridFS
        fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db_manager.get_db(), bucket_name="images")
        content = await image.read()
        image_id = await fs.upload_from_stream(
            filename=image.filename,
            source=content,
            metadata={"type": "poi_image", "content_type": image.content_type}
        )
        image_id = str(image_id)

    # Build POI data
    poi_data = {
        "type": poi_type,
        "title": title,
        "description": description,
        "position": {"x": x, "y": y, "z": z},
        "rotation": {"x": rotation_x, "y": rotation_y, "z": rotation_z},
        "scale": {"x": scale_x, "y": scale_y, "z": scale_z},
        "visible": visible,
        "image_id": image_id,
        "target_scene_id": target_scene_id,
        "media_url": media_url,
        "media_type": media_type
    }

    # Create POI
    poi_id = await db_manager.create_poi(scene_oid, poi_data)

    return JSONResponse(
        status_code=201,
        content={
            "message": "POI created successfully",
            "poi_id": str(poi_id)
        }
    )


@router.get("/space/pois/{scene_id}")
async def get_pois(
    request: Request,
    scene_id: str,
    auth_user=Depends(get_current_user)
):
    """
    Get all POIs for a scene.
    Any viewer can access this.
    """
    if not auth_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    scene_oid = validate_object_id(scene_id)

    # Get space_id from scene to check access
    space = await db_manager.get_collection('spaces').find_one(
        {f"scenes.{scene_id}": {"$exists": True}}
    )
    if not space:
        raise HTTPException(status_code=404, detail="Space not found for scene")

    # Check if user has access (any viewer role)
    user_id = str(auth_user.id)
    if user_id not in space['viewers']:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get POIs
    pois = await db_manager.get_pois(scene_oid)

    # Convert ObjectIds to strings for JSON response
    for poi in pois:
        if 'poi_id' in poi:
            poi['poi_id'] = str(poi['poi_id'])
        if 'image_id' in poi and poi['image_id']:
            poi['image_id'] = str(poi['image_id'])
        if 'created_at' in poi:
            poi['created_at'] = poi['created_at'].isoformat()
        if 'updated_at' in poi:
            poi['updated_at'] = poi['updated_at'].isoformat()

    return JSONResponse(content={"pois": pois})


@router.put("/space/poi/update/{scene_id}/{poi_id}")
async def update_poi(
    request: Request,
    scene_id: str,
    poi_id: str,
    poi_update: UpdatePOIForm,
    auth_user=Depends(get_current_user)
):
    """
    Update a POI.
    Only users with Editor permission can update POIs.
    """
    if not auth_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    scene_oid = validate_object_id(scene_id)
    poi_oid = validate_object_id(poi_id)

    # Get space_id from scene
    space = await db_manager.get_collection('spaces').find_one(
        {f"scenes.{scene_id}": {"$exists": True}}
    )
    if not space:
        raise HTTPException(status_code=404, detail="Space not found for scene")

    # Check Editor permission
    user_id = str(auth_user.id)
    if not await check_editor_permission(space['_id'], user_id):
        raise HTTPException(status_code=403, detail="Editor permission required")

    # Build update data (only include provided fields)
    update_data = {}
    if poi_update.title is not None:
        update_data['title'] = poi_update.title
    if poi_update.description is not None:
        update_data['description'] = poi_update.description

    # Update position if any coordinate is provided
    if any([poi_update.x is not None, poi_update.y is not None, poi_update.z is not None]):
        # Get existing POI to merge with new values
        existing_poi = await db_manager.get_poi(scene_oid, poi_oid)
        if existing_poi:
            position = existing_poi.get('position', {})
            if poi_update.x is not None:
                position['x'] = poi_update.x
            if poi_update.y is not None:
                position['y'] = poi_update.y
            if poi_update.z is not None:
                position['z'] = poi_update.z
            update_data['position'] = position

    # Update rotation if any value is provided
    if any([poi_update.rotation_x is not None, poi_update.rotation_y is not None, poi_update.rotation_z is not None]):
        existing_poi = await db_manager.get_poi(scene_oid, poi_oid)
        if existing_poi:
            rotation = existing_poi.get('rotation', {})
            if poi_update.rotation_x is not None:
                rotation['x'] = poi_update.rotation_x
            if poi_update.rotation_y is not None:
                rotation['y'] = poi_update.rotation_y
            if poi_update.rotation_z is not None:
                rotation['z'] = poi_update.rotation_z
            update_data['rotation'] = rotation

    # Update scale if any value is provided
    if any([poi_update.scale_x is not None, poi_update.scale_y is not None, poi_update.scale_z is not None]):
        existing_poi = await db_manager.get_poi(scene_oid, poi_oid)
        if existing_poi:
            scale = existing_poi.get('scale', {})
            if poi_update.scale_x is not None:
                scale['x'] = poi_update.scale_x
            if poi_update.scale_y is not None:
                scale['y'] = poi_update.scale_y
            if poi_update.scale_z is not None:
                scale['z'] = poi_update.scale_z
            update_data['scale'] = scale

    if poi_update.visible is not None:
        update_data['visible'] = poi_update.visible
    if poi_update.target_scene_id is not None:
        update_data['target_scene_id'] = poi_update.target_scene_id
    if poi_update.media_url is not None:
        update_data['media_url'] = poi_update.media_url
    if poi_update.media_type is not None:
        update_data['media_type'] = poi_update.media_type

    # Update POI
    success = await db_manager.update_poi(scene_oid, poi_oid, update_data)

    if not success:
        raise HTTPException(status_code=404, detail="POI not found")

    return JSONResponse(content={"message": "POI updated successfully"})


@router.delete("/space/poi/delete/{scene_id}/{poi_id}")
async def delete_poi(
    request: Request,
    scene_id: str,
    poi_id: str,
    auth_user=Depends(get_current_user)
):
    """
    Delete a POI.
    Only users with Editor permission can delete POIs.
    """
    if not auth_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    scene_oid = validate_object_id(scene_id)
    poi_oid = validate_object_id(poi_id)

    # Get space_id from scene
    space = await db_manager.get_collection('spaces').find_one(
        {f"scenes.{scene_id}": {"$exists": True}}
    )
    if not space:
        raise HTTPException(status_code=404, detail="Space not found for scene")

    # Check Editor permission
    user_id = str(auth_user.id)
    if not await check_editor_permission(space['_id'], user_id):
        raise HTTPException(status_code=403, detail="Editor permission required")

    # Delete POI
    success = await db_manager.delete_poi(scene_oid, poi_oid)

    if not success:
        raise HTTPException(status_code=404, detail="POI not found")

    return JSONResponse(content={"message": "POI deleted successfully"})


@router.get("/space/scenes/{space_id}")
async def get_scenes(
    request: Request,
    space_id: str,
    auth_user=Depends(get_current_user)
):
    """
    Get all scenes in a space (for link POI target selection).
    Any viewer can access this.
    """
    if not auth_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    space_oid = validate_object_id(space_id)
    space = await db_manager.get_space(space_oid)

    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    # Check if user has access
    user_id = str(auth_user.id)
    if user_id not in space.viewers:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get scene names and IDs
    scenes = []
    for scene_id, scene_name in space.scenes.items():
        scenes.append({
            "id": scene_id,
            "name": scene_name
        })

    return JSONResponse(content={"scenes": scenes})
