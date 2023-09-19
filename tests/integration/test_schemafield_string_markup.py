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

    schema.check_values({"entry": "00:B9:FA:E9:51:0A"})


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
        schema.check_values({"entry": "GZ:B9:FA:E9:51:0A"})


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
        schema.check_values({"entry": "FA:E9:51:0A"})


def test_phonefield_accepts_idn():
    schema = Schema(
        **{
            "uuid": str(uuid4()),
            "name": "Schema",
            "code": "schema",
            "fields": [
                {
                    "name": "entry",
                    "format": {
                        "type": "phone",
                    },
                },
            ],
        }
    )

    schema.check_values({"entry": "0011 (407) 934-7639"})
    schema.check_values({"entry": "(+612) 8881 1480"})
    schema.check_values({"entry": "+61 2 8881 1480"})
    schema.check_values({"entry": "02 8881 1480"})
    schema.check_values({"entry": "131 241"})
    schema.check_values({"entry": "(407) 560-2547"})

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry": "131 HELP"})

    with pytest.raises(SchemaValuesError):
        schema.check_values({"entry": "Not a Phone number"})
