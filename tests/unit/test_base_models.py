from bstk_datatables.table import Table
from bstk_datatables.entry import Entry
from bstk_datatables.schema import Schema
from bstk_datatables.enum import Enum

from uuid import uuid4


def test_load_base_tablestruct():
    data = {
        "uuid": str(uuid4()),
        "name": "Data Table",
        "references": {"entity_uuid": str(uuid4())},
        "connectors": {"connector1": "connectorclass"},
    }
    table = Table(**data)
    assert isinstance(table, Table)
    for field, val in data.items():
        assert getattr(table, field) == val


def test_load_base_entrystruct():
    data = {
        "uuid": str(uuid4()),
        "name": "Data Entry",
        "references": {"entity_uuid": str(uuid4())},
        "connector_references": {"connector1": "connector_ref"},
        "schema": ["base"],
        "values": {"base/value1": "XG230"},
    }
    entry = Entry(**data)
    assert isinstance(entry, Entry)
    for field, val in data.items():
        assert getattr(entry, field) == val


def test_load_base_schemastruct():
    data = {
        "uuid": str(uuid4()),
        "references": {"entity_uuid": str(uuid4())},
        "name": "Base Schema",
        "code": "base",
        "fields": [
            {
                "name": "text_value",
                "format": {
                    "type": "text",
                },
            },
            {
                "name": "number_value",
                "format": {
                    "type": "number",
                },
            },
            {
                "name": "boolean_value",
                "format": {
                    "type": "bool",
                },
            },
            {
                "name": "localenum_value",
                "format": {
                    "type": "enum",
                    "values": [
                        "Local Enum Value 1",
                        "Local Enum Value 2",
                        "Local Enum Value 3",
                    ],
                },
            },
            {
                "name": "enum_value",
                "format": {
                    "type": "enum",
                    "lookup": "test_enum",
                },
            },
            {"name": "date_value", "format": {"type": "datetime"}},
        ],
    }
    schema = Schema(**data)
    assert isinstance(schema, Schema)
    for field, val in data.items():
        assert getattr(schema, field) == val


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
        assert getattr(enum, field) == val
