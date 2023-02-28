from uuid import uuid4

import pytest

from bstk_datatables.schema import Schema, SchemaValuesError


def test_macaddressfield_accepts_mac():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "mac_address",
                    },
                },
            ],
        }
    )

    schema.process_values({"entry": "00:B9:FA:E9:51:0A"})


def test_macaddressfield_rejects_invalid_mac():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "mac_address",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.process_values({"entry": "GZ:B9:FA:E9:51:0A"})


def test_macaddressfield_rejects_tooshort_mac():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "mac_address",
                    },
                },
            ],
        }
    )

    with pytest.raises(SchemaValuesError):
        schema.process_values({"entry": "FA:E9:51:0A"})
