from uuid import uuid4

import pytest

from bstk_datatables.schema import Schema, SchemaValuesError


def test_field_is_required():
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
                    "format": {"type": "text", "required": True},
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry1": "text"})

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry1": "text", "entry2": None})

    schema.check_values({"entry2": "value"})
