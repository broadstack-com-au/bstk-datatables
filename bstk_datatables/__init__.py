import typing

from marshmallow import fields as marshmallow_fields

SCHEMAFIELD_MAP: typing.Dict[typing.AnyStr, typing.Callable] = {
    "text": marshmallow_fields.String,
    "number": marshmallow_fields.Number,
    "bool": marshmallow_fields.Boolean,
    "enum": marshmallow_fields.Enum,
    "datetime": marshmallow_fields.AwareDateTime,
}
