from uuid import uuid4

import pytest

from bstk_datatables.schema import Schema, SchemaValuesError


def test_emailfield_accepts_email():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "email",
                    },
                },
            ],
        }
    )

    schema.check_values({"entry": "a@b.com"})


def test_emailfield_rejects_float():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "email",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry": "1.1"})


def test_emailfield_rejects_string():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "email",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry": "1.1a"})


def test_emailfield_rejects_bool():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "email",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry": False})
