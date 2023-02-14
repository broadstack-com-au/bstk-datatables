from __future__ import annotations

import typing

from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields as marshmallow_fields

SCHEMAFIELD_MAP: typing.Dict[typing.AnyStr, typing.Callable] = {
    "text": marshmallow_fields.String,
    "number": marshmallow_fields.Number,
    "bool": marshmallow_fields.Boolean,
    "enum": marshmallow_fields.Enum,
    "datetime": marshmallow_fields.AwareDateTime,
}


def export(
    model: typing.Union[Entry, Enum, Schema, Table]  # noqa: F821
) -> typing.Dict[typing.AnyStr, typing.Any]:
    return model.export()


def convert_to_marshmallow(
    schema: typing.Union[Schema, MergedSchema]  # noqa: F821
) -> MarshmallowSchema:
    _schema_struct = {}
    for _schemafield in schema.fields:
        _schema_struct[_schemafield.name] = _schemafield.format._field

    return MarshmallowSchema.from_dict(_schema_struct, name=schema.name)
