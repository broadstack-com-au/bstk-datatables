from __future__ import annotations

import copy
import typing
from dataclasses import dataclass, field

from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields as marshmallow_fields

from . import SCHEMAFIELD_EXTATTR, SCHEMAFIELD_MAP, name_to_code, schema_to_marshmallow
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
    code: typing.Optional[typing.AnyStr] = field(default=None)
    references: typing.Optional[typing.Dict[typing.AnyStr, typing.Any]] = field(
        default=None
    )
    fields: typing.Optional[
        typing.List[typing.Union[SchemaField, typing.Dict[typing.AnyStr, typing.Any]]]
    ] = field(default=None)
    _field_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    _schema: MarshmallowSchema = field(init=False, default=None)
    _missing_lookups: typing.Dict[
        typing.AnyStr, typing.List[SchemaFieldFormat]
    ] = field(init=False, default=None)

    def __post_init__(self):
        self._missing_lookups = {}
        self._field_list = []

        if not self.code:
            self.code = name_to_code(self.name)

        if not self.fields:
            self.fields = []
            return

        _fields = copy.deepcopy(self.fields)
        self.fields = []
        for _field_data in _fields:
            if isinstance(_field_data, SchemaField):
                self.add_field(_field_data)
            else:
                self.add_field(SchemaField(**_field_data))

        for _field in self.fields:
            if _field.format._missing_lookup:
                if _field.format.lookup not in self._missing_lookups:
                    self._missing_lookups[_field.format.lookup] = []
                self._missing_lookups[_field.format.lookup].append(_field.format)

        if not self._missing_lookups:
            self._schema = schema_to_marshmallow(self)

    def attach_lookup(self, lookup: Enum) -> None:
        if lookup.code not in self._missing_lookups:
            raise ValueError(f"Invalid lookup reference `{lookup.code}")
        for _missing_lookup in self._missing_lookups[lookup.code]:
            _missing_lookup.attach_lookup(lookup)
        del self._missing_lookups[lookup.code]

        if len(self._missing_lookups) < 1:
            self._schema = schema_to_marshmallow(self)

    def add_field(self, schema_field: SchemaField) -> None:
        if schema_field.code in self._field_list:
            raise ValueError(f"Duplicate field name `{schema_field.name}`")
        self._field_list.append(schema_field.code)
        self.fields.append(schema_field)

    def set_fields(self, schema_fields: typing.List(SchemaField)):
        self._field_list = []
        self.fields = []
        for schema_field in schema_fields:
            self.add_field(schema_field)

    def process_values(self, values: typing.Dict) -> None:
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
    code: typing.AnyStr = field(default=None)
    _value: typing.Any = field(init=False, default=None)

    def __post_init__(self):
        if not self.code:
            self.code = name_to_code(self.name)

        self.format = SchemaFieldFormat(**self.format)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        return {
            "name": self.__dict__["name"],
            "code": self.__dict__["code"],
            "format": self.format.export(),
        }


@dataclass
class SchemaFieldFormat:
    type: typing.Optional[typing.AnyStr]
    values: typing.Optional[typing.Any] = None
    lookup: typing.Optional[typing.Any] = None
    required: typing.Optional[bool] = field(default=False)
    _field: marshmallow_fields.Field = field(init=False, default=None)
    _missing_lookup: bool = field(init=False, default=False)

    def __post_init__(self):
        self._generate_marshmallow_field()

    def attach_lookup(
        self, lookup_value: typing.Union[typing.List[typing.AnyStr], PyEnum]
    ):
        self.lookup = lookup_value
        self._generate_marshmallow_field()

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        _fields = ["type", "values", "lookup", "required"]
        rtn = {}
        for _exportfield in _fields:
            if _exportfield == "lookup" and isinstance(
                self.__dict__[_exportfield], Enum
            ):
                rtn[_exportfield] = self.__dict__[_exportfield].code
                continue
            if self.__dict__[_exportfield]:
                rtn[_exportfield] = self.__dict__[_exportfield]
        return rtn

    def _get_mapped_fieldclass(self) -> typing.Callable:
        if self.type in SCHEMAFIELD_MAP:
            return SCHEMAFIELD_MAP[self.type]

        raise ValueError(f"Field format type `{self.type}` is invalid")

    def _get_field_params(self) -> typing.Union[None, typing.Dict]:
        _field_params = {}
        if self.required is not None:
            _field_params["required"] = self.required
        if self.type == "enum":
            self._missing_lookup = False
            if self.values:
                _field_params["enum"] = PyEnum("enum", self.values)
            elif self.lookup and isinstance(self.lookup, Enum):
                _field_params["enum"] = self.lookup.values
            else:
                self._missing_lookup = True
                return None

        if self.type not in SCHEMAFIELD_EXTATTR:
            return _field_params

        return {**_field_params, **SCHEMAFIELD_EXTATTR[self.type]}

    def _generate_marshmallow_field(self):
        _field_params = self._get_field_params()
        if _field_params is None:
            return

        self._field = self._get_mapped_fieldclass()(**_field_params)
