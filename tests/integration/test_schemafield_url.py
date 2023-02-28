from uuid import uuid4

import pytest

from bstk_datatables.schema import Schema, SchemaValuesError


def test_urlfield_accepts_proto():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "url",
                    },
                },
            ],
        }
    )

    schema.process_values({"entry": "https://127.0.0.1/"})


def test_urlfield_rejects_plain_ip():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "url",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.process_values({"entry": "127.0.0.1"})


def test_urlfield_rejects_invalid_proto():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "url",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.process_values({"entry": "mms://127.0.0.1"})


def test_urlfield_accepts_extended_proto():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "url",
                    },
                },
            ],
        }
    )

    schema.process_values({"entry": "tcp://127.0.0.1"})


def test_urlfield_rejects_nonstatedproto():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "url",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.process_values({"entry": "127.0.0.1:8080"})
