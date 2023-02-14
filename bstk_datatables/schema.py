from __future__ import annotations

import copy
import typing
from dataclasses import dataclass, field

from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields as marshmallow_fields

from . import SCHEMAFIELD_MAP, convert_to_marshmallow
from .enum import Enum, PyEnum


class SchemaValuesError(Exception):
    errors: typing.Dict[typing.AnyStr, typing.List[typing.AnyStr]]

    def __init__(
        self,
        *args: object,
        errors: typing.Dict[typing.AnyStr, typing.List[typing.AnyStr]],
    ) -> None:
        self.errors = errors
        super().__init__(*args)


@dataclass
class Schema:
    uuid: typing.AnyStr
    name: typing.AnyStr
    code: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    fields: typing.List[
        typing.Union[SchemaField, typing.Dict[typing.AnyStr, typing.Any]]
    ]
    _field_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    _schema: MarshmallowSchema = field(init=False, default=None)

    def __post_init__(self):
        _fields = copy.deepcopy(self.fields)
        self.fields = []
        self._field_list = []
        for _field_data in _fields:
            if isinstance(_field_data, SchemaField):
                self.add_field(_field_data)
            else:
                self.add_field(SchemaField(**_field_data))
        self._schema = convert_to_marshmallow(self)

    def add_field(self, schema_field: SchemaField):
        if schema_field.name in self._field_list:
            raise ValueError(f"Duplicate field name `{schema_field.name}`")
        self._field_list.append(schema_field.name)
        self.fields.append(schema_field)

    def process_values(self, values: typing.Dict) -> typing.NoReturn:
        _schema: MarshmallowSchema = self._schema()
        failures = _schema.validate(data=values)
        if not failures:
            return

        raise SchemaValuesError(errors=failures)

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        _fields = ["uuid", "name", "code", "references"]
        rtn = {}
        for _exportfield in _fields:
            rtn[_exportfield] = self.__dict__[_exportfield]
        rtn["fields"] = [_field.export() for _field in self.fields]
        return rtn


@dataclass
class SchemaField:
    name: typing.AnyStr
    format: SchemaFieldFormat
    _value: typing.Any = field(init=False, default=None)

    def __post_init__(self):
        self.format = SchemaFieldFormat(**self.format)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        return {"name": self.__dict__["name"], "format": self.format.export()}


@dataclass
class SchemaFieldFormat:
    type: typing.Optional[typing.AnyStr]
    values: typing.Optional[typing.Any] = None
    lookup: typing.Optional[typing.Any] = None
    _field: marshmallow_fields.Field = field(init=False, default=None)

    @staticmethod
    def _get_mapped_fieldclass(type: typing.AnyStr) -> typing.Callable:
        if type in SCHEMAFIELD_MAP:
            return SCHEMAFIELD_MAP[type]

        raise ValueError(f"Field format type `{type}` is invalid")

    def __post_init__(self):
        _field_params = {}

        if self.type == "enum":
            if self.values:
                _field_params["enum"] = PyEnum("enum", self.values)
            elif self.lookup and isinstance(self.lookup, Enum):
                _field_params["enum"] = self.lookup.values
            else:
                return

        self._field = self._get_mapped_fieldclass(self.type)(**_field_params)

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        _fields = ["type", "values", "lookup"]
        rtn = {}
        for _exportfield in _fields:
            if self.__dict__[_exportfield]:
                rtn[_exportfield] = self.__dict__[_exportfield]
        return rtn
