from datetime import datetime, timezone
from uuid import uuid4

import pytest

from bstk_datatables import export
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
            "code": "text_value",
            "format": {
                "type": "text",
            },
        },
        {
            "name": "number_value",
            "code": "number_value",
            "format": {
                "type": "number",
            },
        },
        {
            "name": "boolean_value",
            "code": "boolean_value",
            "format": {
                "type": "bool",
            },
        },
        {
            "name": "localenum_value",
            "code": "localenum_value",
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
            "code": "enum_value",
            "format": {
                "type": "enum",
                "lookup": "test_enum",
            },
        },
        {"name": "date_value", "code": "date_value", "format": {"type": "datetime"}},
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


def test_export_base_schema():
    schema = Schema(**_schemadata)
    exported = export(schema)
    assert exported == _schemadata


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
                    "code": "enum_value",
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
        schema.process_values(bad_data)

    good_data = {
        "enum_value": "Enum Value 3",
    }

    schema.process_values(good_data)


def test_export_schema_with_lookups():
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

    _lookupschemadata = {
        "uuid": str(uuid4()),
        "references": {"entity_uuid": str(uuid4())},
        "name": "Base Schema",
        "code": "base",
        "fields": [
            {
                "name": "enum_value",
                "code": "enum_value",
                "format": {
                    "type": "enum",
                    "lookup": lookedup_enum,
                },
            },
        ],
    }
    schema = Schema(**_lookupschemadata)
    exported = export(schema)
    _lookupschemadata["fields"][0]["format"]["lookup"] = "test_enum"
    assert exported == _lookupschemadata


def test_schema_accepts_valid_data():
    schema = Schema(**_schemadata)
    schema.attach_lookup(
        Enum(
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
    )
    data = {
        "text_value": "text",
        "number_value": 1,
        "boolean_value": False,
        "localenum_value": "Local Enum Value 1",
        "date_value": str(datetime.now(timezone.utc)),
    }

    schema.process_values(data)


def test_schema_invalidates_data():
    schema = Schema(**_schemadata)
    schema.attach_lookup(
        Enum(
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
    )
    invalid_data = {
        "text_value": True,
        "number_value": False,
        "boolean_value": "nope",
        "localenum_value": "invalid",
        "date_value": "June 3rd",
    }

    with pytest.raises(SchemaValuesError):
        schema.process_values(invalid_data)

    try:
        schema.process_values(invalid_data)
    except SchemaValuesError as e:
        for key in invalid_data.keys():
            assert key in e.errors


def test_schemafieldformat_flags_missing_lookup():
    _field = SchemaFieldFormat(
        **{
            "type": "enum",
            "lookup": "lookup_name",
        }
    )
    assert _field._missing_lookup is True


def test_schemafieldformat_accepts_lookup():
    _field = SchemaFieldFormat(
        **{
            "type": "enum",
            "lookup": "lookup_name",
        }
    )
    assert _field._missing_lookup is True

    _lookup = Enum(
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
    _field.attach_lookup(_lookup)
    assert _field._missing_lookup is False


def test_schema_multilookup_attachment():
    _lookupschema = {
        "uuid": str(uuid4()),
        "references": {"entity_uuid": str(uuid4())},
        "name": "Base Schema",
        "code": "base",
        "fields": [
            {
                "name": "lookup_one",
                "code": "lookup_one",
                "format": {"type": "enum", "lookup": "test_enum"},
            },
            {
                "name": "lookup_two",
                "code": "lookup_two",
                "format": {"type": "enum", "lookup": "test_enum"},
            },
        ],
    }
    schema = Schema(**_lookupschema)
    schema.attach_lookup(
        Enum(
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
    )
    assert not schema._missing_lookups

    for field in schema.fields:
        assert isinstance(field.format.lookup, Enum)

    _export = schema.export()
    assert _lookupschema == _export
