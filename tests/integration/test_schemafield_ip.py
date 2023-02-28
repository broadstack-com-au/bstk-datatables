from uuid import uuid4

import pytest

from bstk_datatables.schema import Schema, SchemaValuesError


def test_ipfield_accepts_ipv4():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "ip",
                    },
                },
            ],
        }
    )

    schema.process_values({"entry": "127.0.0.1"})


def test_ipfield_accepts_ipv4_masked():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "ip",
                    },
                },
            ],
        }
    )

    schema.process_values({"entry": "127.0.0.1/24"})


def test_ipfield_accepts_ipv6():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "ip",
                    },
                },
            ],
        }
    )

    schema.process_values({"entry": r"fe80::3c22:fbff:fe2a:9d64"})


def test_ipfield_rejects_ipv4_invalidmask():
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
        schema.process_values({"entry": "127.0.0.1/64"})


def test_ipfield_rejects_crap():
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
        schema.process_values({"entry": "localhost"})
