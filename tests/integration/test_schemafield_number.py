from uuid import uuid4

import pytest

from bstk_datatables.schema import Schema, SchemaValuesError


def test_numberfield_accepts_int():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "number",
                    },
                },
            ],
        }
    )

    schema.check_values({"entry": "1"})


def test_numberfield_accepts_float():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "number",
                    },
                },
            ],
        }
    )

    schema.check_values({"entry": "1.1"})


def test_numberfield_rejects_string():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "number",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry": "1.1a"})


def test_numberfield_rejects_bool():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "number",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry": False})
