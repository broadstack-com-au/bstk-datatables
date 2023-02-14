from enum import EnumMeta
from uuid import uuid4

from bstk_datatables import export
from bstk_datatables.enum import Enum


def test_load_enum():
    data = {
        "uuid": str(uuid4()),
        "references": {"entity_uuid": str(uuid4())},
        "code": "test_enum",
        "name": "Test Enum",
        "values": [
            "Enum Value 1",
            "Enum Value 2",
            "Enum Value 3",
        ],
    }
    enum = Enum(**data)
    assert isinstance(enum, Enum)
    for field, val in data.items():
        if field != "values":
            assert getattr(enum, field) == val
            continue

        assert isinstance(getattr(enum, field), EnumMeta)


def test_enum_export():
    data = {
        "uuid": str(uuid4()),
        "references": {"entity_uuid": str(uuid4())},
        "code": "test_enum",
        "name": "Test Enum",
        "values": [
            "Enum Value 1",
            "Enum Value 2",
            "Enum Value 3",
        ],
    }
    enum = Enum(**data)
    exported = export(enum)
    assert exported == data
