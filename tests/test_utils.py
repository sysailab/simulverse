import pytest
from bson.objectid import ObjectId
from fastapi import HTTPException

from app.core.libs.utils import validate_object_id


def test_validate_object_id_from_string():
    oid = ObjectId()
    assert validate_object_id(str(oid)) == oid

def test_validate_object_id_from_object():
    oid = ObjectId()
    assert validate_object_id(oid) is oid

def test_validate_object_id_invalid_input():
    with pytest.raises(HTTPException) as exc:
        validate_object_id('invalid-object-id')
    assert exc.value.status_code == 400

