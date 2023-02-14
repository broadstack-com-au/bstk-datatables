from datetime import datetime, timezone
from uuid import uuid4

import pytest

from bstk_datatables.enum import Enum
from bstk_datatables.schema import (
    Schema,
    SchemaField,
    SchemaFieldFormat,
    SchemaValuesError,
)

_schemadata = {
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


def test_load_base_schemastruct():
    schema = Schema(**_schemadata)
    assert isinstance(schema, Schema)
    for field, val in _schemadata.items():
        if field != "fields":
            assert getattr(schema, field) == val
            continue

        for fieldval in getattr(schema, field):
            assert isinstance(fieldval, SchemaField)
            assert isinstance(fieldval.format, SchemaFieldFormat)

            if fieldval.format.type == "enum":
                assert fieldval.format.lookup or fieldval.format.values


def test_schema_accepts_lookupenum():
    lookedup_enum = Enum(
        **{
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
    )

    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "references": {"entity_uuid": str(uuid4())},
            "name": "Base Schema",
            "code": "base",
            "fields": [
                {
                    "name": "enum_value",
                    "format": {
                        "type": "enum",
                        "lookup": lookedup_enum,
                    },
                },
            ],
        }
    )

    bad_data = {
        "enum_value": "Enum Value 99",
    }

    with pytest.raises(SchemaValuesError):
        schema.set_values(bad_data)

    good_data = {
        "enum_value": "Enum Value 3",
    }

    schema.set_values(good_data)


def test_schema_validates_data():
    schema = Schema(**_schemadata)
    data = {
        "text_value": "text",
        "number_value": 1,
        "boolean_value": False,
        "localenum_value": "Local Enum Value 1",
        "date_value": str(datetime.now(timezone.utc)),
    }

    schema.set_values(data)


def test_schema_invalidates_data():
    schema = Schema(**_schemadata)
    invalid_data = {
        "text_value": True,
        "number_value": False,
        "boolean_value": "nope",
        "localenum_value": "invalid",
        "date_value": "June 3rd",
    }

    with pytest.raises(SchemaValuesError):
        schema.set_values(invalid_data)

    try:
        schema.set_values(invalid_data)
    except SchemaValuesError as e:
        for key in invalid_data.keys():
            assert key in e.errors
