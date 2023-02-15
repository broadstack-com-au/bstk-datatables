import typing
from dataclasses import dataclass, field

from marshmallow import Schema as MarshmallowSchema

from . import convert_to_marshmallow
from .enum import Enum
from .schema import Schema, SchemaField, SchemaFieldFormat, SchemaValuesError


@dataclass
class MergedSchema:
    schemata: typing.List[typing.Union[typing.Dict[typing.AnyStr, typing.Any], Schema]]
    name: typing.AnyStr = field(default=None)
    _schema_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    fields: typing.List[SchemaField] = field(init=False, default=None)
    _field_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    _schema: MarshmallowSchema = field(init=False, default=None)
    _missing_lookups: typing.Dict[
        typing.AnyStr, typing.List[SchemaFieldFormat]
    ] = field(init=False, default=None)

    def __post_init__(self):
        if len(self.schemata) < 1:
            return

        self._missing_lookups = {}
        self._schema_list = []
        self.fields = []
        self._field_list = []
        for schema in self.schemata:
            if isinstance(schema, Schema):
                self.add_field(_field for _field in schema.fields)
                self._schema_list.append(schema.name)

            if "fields" in schema:
                _schemaname = f"schema_{len(self._schema_list)}"
                if "name" in schema:
                    _schemaname = schema["name"]
                self._schema_list.append(_schemaname)
                for dictfield in schema["fields"]:
                    self.add_field(SchemaField(**dictfield))

        for _field in self.fields:
            if _field.format._missing_lookup:
                if _field.format.lookup not in self._missing_lookups:
                    self._missing_lookups[_field.format.lookup] = []
                self._missing_lookups[_field.format.lookup].append(_field.format)

        self.name = f"Merged schema: {', '.join(self._schema_list)}"
        if not self._missing_lookups:
            self._schema = convert_to_marshmallow(self)

    def add_lookup(self, lookup: Enum) -> None:
        if lookup.code not in self._missing_lookups:
            raise ValueError(f"Invalid lookup reference `{lookup.code}")
        for _missing_lookup in self._missing_lookups[lookup.code]:
            _missing_lookup.attach_lookup(lookup)
        del self._missing_lookups[lookup.code]

        if len(self._missing_lookups) < 1:
            self._schema = convert_to_marshmallow(self)

    def add_field(self, new_field: SchemaField) -> None:
        if new_field.name in self._field_list:
            # Duplicates are expected here because we're merging
            return
        self._field_list.append(new_field.name)
        self.fields.append(new_field)

    def process_values(self, values: typing.Dict) -> None:
        schema: MarshmallowSchema = self._schema()
        failures = schema.validate(data=values)
        if failures:
            raise SchemaValuesError(errors=failures)
