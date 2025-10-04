from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.routers import space as space_router


def make_space(viewers):
    return SimpleNamespace(viewers=viewers)


def test_ensure_member_allows_registered_viewer():
    space = make_space({"user": "Viewer"})
    assert space_router._ensure_member(space, "user") == "Viewer"

def test_ensure_member_rejects_unknown_user():
    space = make_space({})
    with pytest.raises(HTTPException) as exc:
        space_router._ensure_member(space, "missing")
    assert exc.value.status_code == 403

def test_ensure_editor_requires_editor_role():
    space = make_space({"user": "Viewer"})
    with pytest.raises(HTTPException) as exc:
        space_router._ensure_editor(space, "user")
    assert exc.value.status_code == 403

def test_ensure_editor_allows_editor():
    space = make_space({"user": "Editor"})
    assert space_router._ensure_editor(space, "user") == "Editor"

