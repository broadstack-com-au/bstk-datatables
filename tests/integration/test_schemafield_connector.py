from uuid import uuid4

import pytest

from bstk_datatables.schema import Schema, SchemaValuesError


def test_connector_field_entry_processing():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry1",
                    "format": {"type": "text", "required": False},
                },
                {
                    "name": "entry2",
                    "format": {"type": "connector", "required": True},
                },
                {
                    "name": "entry3",
                    "format": {
                        "type": "connector",
                        "required": True,
                        "connector_data": {""},
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry1": "text"})

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry1": "text", "entry2": None})

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry2": "value"})
