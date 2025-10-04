import asyncio

import pytest
from starlette.datastructures import FormData

from app.core.schemas.poi_model import CreatePOIForm


class DummyRequest:
    def __init__(self, data: dict[str, str]):
        self._data = FormData(data)

    async def form(self):
        return self._data


def test_create_poi_form_validates_and_builds_document():
    request = DummyRequest(
        {
            "poi_type": "info",
            "title": "Test POI",
            "description": "설명",
            "position_x": "1.2",
            "position_y": "1.5",
            "position_z": "-3",
            "rotation_x": "0",
            "rotation_y": "45",
            "rotation_z": "0",
            "scale_x": "1",
            "scale_y": "1",
            "scale_z": "1",
        }
    )
    form = CreatePOIForm(request)
    asyncio.run(form.load_data())
    assert asyncio.run(form.is_valid()) is True
    document = form.to_document()
    assert document["title"] == "Test POI"
    assert document["position"]["x"] == pytest.approx(1.2)
    assert document["rotation"]["y"] == pytest.approx(45)
    assert document["visible"] is True


def test_create_poi_form_rejects_unknown_type():
    request = DummyRequest({"poi_type": "unknown", "title": ""})
    form = CreatePOIForm(request)
    asyncio.run(form.load_data())
    assert asyncio.run(form.is_valid()) is False
    assert form.errors

