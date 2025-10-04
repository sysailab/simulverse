from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId


ALLOWED_POI_TYPES = {"info", "link", "media"}


class CreatePOIForm:
    """Parse and validate POI creation form submissions."""

    def __init__(self, request):
        self.request = request
        self.errors: list[str] = []
        self._raw: Dict[str, Any] = {}
        self._cleaned: Dict[str, Any] | None = None

    async def load_data(self) -> None:
        form = await self.request.form()
        self._raw = {k: form.get(k) for k in form.keys()}

    async def is_valid(self) -> bool:
        poi_type = (self._raw.get("poi_type") or "info").lower()
        if poi_type not in ALLOWED_POI_TYPES:
            self.errors.append("POI type은 info, link, media 중 하나여야 합니다.")
        title = (self._raw.get("title") or "").strip()
        if not title:
            self.errors.append("제목을 입력해주세요.")
        description = (self._raw.get("description") or "").strip()

        position = self._parse_vector("position", default=(0.0, 1.3, -3.0))
        rotation = self._parse_vector("rotation", default=(0.0, 0.0, 0.0))
        scale = self._parse_vector("scale", default=(1.0, 1.0, 1.0))

        target_scene_id = self._clean_object_id(self._raw.get("target_scene_id"))
        image_id = self._clean_object_id(self._raw.get("image_id"))
        visible = (self._raw.get("visible") == "on") if "visible" in self._raw else True

        if self.errors:
            return False

        now = datetime.utcnow()
        cleaned: Dict[str, Any] = {
            "poi_id": ObjectId(),
            "type": poi_type,
            "title": title,
            "description": description,
            "position": position,
            "rotation": rotation,
            "scale": scale,
            "visible": visible,
            "image_id": image_id,
            "target_scene_id": target_scene_id,
            "created_at": now,
            "updated_at": now,
        }
        self._cleaned = cleaned
        return True

    def to_document(self) -> Dict[str, Any]:
        if self._cleaned is None:
            raise ValueError("Form data has not been validated")
        return dict(self._cleaned)

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._raw)

    def _parse_vector(self, prefix: str, default: tuple[float, float, float]) -> Dict[str, float]:
        x = self._parse_float(self._raw.get(f"{prefix}_x"), f"{prefix} X", default[0])
        y = self._parse_float(self._raw.get(f"{prefix}_y"), f"{prefix} Y", default[1])
        z = self._parse_float(self._raw.get(f"{prefix}_z"), f"{prefix} Z", default[2])
        return {"x": x, "y": y, "z": z}

    def _parse_float(self, value: Optional[str], label: str, default: float) -> float:
        if value is None or value == "":
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            self.errors.append(f"{label} 값은 숫자여야 합니다.")
            return default

    def _clean_object_id(self, value: Optional[str]) -> Optional[ObjectId]:
        if not value:
            return None
        try:
            return ObjectId(value)
        except Exception:
            self.errors.append("ID 형식이 올바르지 않습니다.")
            return None

