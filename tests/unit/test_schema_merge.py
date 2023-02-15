from uuid import uuid4

import pytest

from bstk_datatables import export
from bstk_datatables.merge import MergedSchema, SchemaValuesError

_schemadata = [
    {
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
        ],
    },
    {
        "uuid": str(uuid4()),
        "references": {"entity_uuid": str(uuid4())},
        "name": "Addon Schema",
        "code": "addon",
        "fields": [
            {
                "name": "text_value",
                "format": {
                    "type": "text",
                },
            },
            {
                "name": "additional_number_value",
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
        ],
    },
]

_schemavalues = {
    "text_value": "text",
    "number_value": 100,
    "additional_number_value": 101,
    "boolean_value": True,
}

_invalid_schemavalues = {
    "text_value": False,
    "not_a_field": 100,
    "additional_number_value": "Thursday",
    "boolean_value": 99,
}


def test_process_merged_schema():
    schema = MergedSchema(schemata=_schemadata)
    assert isinstance(schema, MergedSchema)
    for field in schema.fields:
        assert field.name in _schemavalues


def test_merged_schema_noexport():
    schema = MergedSchema(schemata=_schemadata)
    with pytest.raises(Exception):
        export(schema)


def test_merged_schema_accepts_data():
    schema = MergedSchema(schemata=_schemadata)
    assert isinstance(schema, MergedSchema)
    schema.process_values(_schemavalues)


def test_merged_schema_rejects_invalid_data():
    schema = MergedSchema(schemata=_schemadata)
    assert isinstance(schema, MergedSchema)
    with pytest.raises(SchemaValuesError):
        schema.process_values(_invalid_schemavalues)

    try:
        schema.process_values(_invalid_schemavalues)
    except SchemaValuesError as e:
        for key in _invalid_schemavalues.keys():
            assert key in e.errors
