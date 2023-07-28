from __future__ import annotations

import re
import typing

from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields as marshmallow_fields
from marshmallow.validate import Regexp as RegexpValidator

from bstk_datatables.validators.luhn import LuhnValidator

"""
Simple mapping from schemafield types to marshmallow field classes
"""
SCHEMAFIELD_MAP: typing.Dict[typing.AnyStr, typing.Callable] = {
    "bool": marshmallow_fields.Boolean,
    "datetime": marshmallow_fields.AwareDateTime,
    "email": marshmallow_fields.Email,
    "enum": marshmallow_fields.Enum,
    "ip": marshmallow_fields.IPInterface,
    "mac_address": marshmallow_fields.String,
    "number": marshmallow_fields.Number,
    "phone": marshmallow_fields.String,
    "text": marshmallow_fields.String,
    "blob": marshmallow_fields.String,
    "url": marshmallow_fields.Url,
    "luhn": marshmallow_fields.String,
}

"""
Any "default" params that should be injected into the marshmallow field constructor
"""
SCHEMAFIELD_EXTATTR: typing.Dict[
    typing.AnyStr,
    typing.Union[typing.Dict, typing.AnyStr, typing.List, bool, str, int, float],
] = {
    "url": {"schemes": ("http", "https", "ftp", "ftps", "sftp", "ssh", "tcp", "udp")},
    "mac_address": {
        "validate": RegexpValidator(
            regex=r"^([0-9a-f]{2}[:-]){5}[0-9a-f]{2}$", flags=re.IGNORECASE
        ),
    },
    "phone": {
        "validate": RegexpValidator(
            regex=r"^([\(]?[\+0-9]{1,}[)]?)?([0-9 \(\)\.\-]{6,})$"
        )
    },
    "luhn": {"validate": LuhnValidator},
}


def export(
    model: typing.Union[Entry, Enum, Schema, Table]  # noqa: F821
) -> typing.Dict[typing.AnyStr, typing.Any]:
    """
    Dumb wrapper for model exports
    """
    if not hasattr(model, "export") or not callable(model.export):
        raise Exception("Model `{model}` is not exportable")
    return model.export()


def schema_to_marshmallow(
    schema: typing.Union[Schema, MergedSchema]  # noqa: F821
) -> MarshmallowSchema:
    """
    Create a marshmallow schema from either a Schema or MergedSchema
    """
    _schema_struct = {}
    for _schemafield in schema.fields:
        _schema_struct[_schemafield.code] = _schemafield.format._field

    return MarshmallowSchema.from_dict(_schema_struct, name=schema.name)


def name_to_code(name: typing.AnyStr) -> typing.AnyStr:
    """
    dumb snake-caser for code fields
    """
    code = re.sub(r"/(\W)/gm", "", name.replace(" ", "_"))
    return code.lower()
