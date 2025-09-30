"""
POI (Point of Interest) Data Models

Pydantic models for POI system validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from bson import ObjectId
from datetime import datetime


class Position(BaseModel):
    """3D Position coordinates"""
    x: float
    y: float
    z: float


class Rotation(BaseModel):
    """3D Rotation (Euler angles in degrees)"""
    x: float = 0
    y: float = 0
    z: float = 0


class Scale(BaseModel):
    """3D Scale"""
    x: float = 1
    y: float = 1
    z: float = 1


class POIBase(BaseModel):
    """Base POI model with common fields"""
    type: Literal["info", "link", "media"]
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    position: Position
    rotation: Rotation = Field(default_factory=lambda: Rotation())
    scale: Scale = Field(default_factory=lambda: Scale())
    visible: bool = True


class InfoPOI(POIBase):
    """Information POI with optional image"""
    type: Literal["info"] = "info"
    image_id: Optional[str] = None  # GridFS image ID


class LinkPOI(POIBase):
    """Link POI for scene navigation"""
    type: Literal["link"] = "link"
    target_scene_id: str  # ObjectId of target scene


class MediaPOI(POIBase):
    """Media POI for video/audio content"""
    type: Literal["media"] = "media"
    media_url: Optional[str] = None
    media_type: Optional[Literal["video", "audio"]] = None


class CreatePOIForm(BaseModel):
    """Form for creating a new POI"""
    type: Literal["info", "link", "media"]
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    x: float
    y: float
    z: float
    rotation_x: float = 0
    rotation_y: float = 0
    rotation_z: float = 0
    scale_x: float = 1
    scale_y: float = 1
    scale_z: float = 1
    visible: bool = True

    # Type-specific fields
    target_scene_id: Optional[str] = None  # For link POI
    media_url: Optional[str] = None  # For media POI
    media_type: Optional[Literal["video", "audio"]] = None  # For media POI


class UpdatePOIForm(BaseModel):
    """Form for updating an existing POI"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    rotation_x: Optional[float] = None
    rotation_y: Optional[float] = None
    rotation_z: Optional[float] = None
    scale_x: Optional[float] = None
    scale_y: Optional[float] = None
    scale_z: Optional[float] = None
    visible: Optional[bool] = None

    # Type-specific fields
    target_scene_id: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[Literal["video", "audio"]] = None


class POIResponse(BaseModel):
    """POI response model with all fields including IDs"""
    poi_id: str
    type: str
    title: str
    description: Optional[str] = None
    position: Position
    rotation: Rotation
    scale: Scale
    visible: bool
    image_id: Optional[str] = None
    target_scene_id: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
