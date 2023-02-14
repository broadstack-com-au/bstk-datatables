import typing
from dataclasses import dataclass, field

from marshmallow import Schema as MarshmallowSchema

from . import convert_to_marshmallow
from .schema import Schema, SchemaField, SchemaValuesError


@dataclass
class MergedSchema:
    schemata: typing.List[typing.Union[typing.Dict[typing.AnyStr, typing.Any], Schema]]
    name: typing.AnyStr = field(default=None)
    _schema_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    fields: typing.List[SchemaField] = field(init=False, default=None)
    _field_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    _schema: MarshmallowSchema = field(init=False, default=None)

    def __post_init__(self):
        if len(self.schemata) < 1:
            return

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

        self.name = f"Merged schema: {', '.join(self._schema_list)}"
        self._schema = convert_to_marshmallow(self)

    def add_field(self, new_field: SchemaField) -> None:
        if new_field.name in self._field_list:
            # Duplicates are expected here because we're merging
            return
        self._field_list.append(new_field.name)
        self.fields.append(new_field)

    def process_values(self, values: typing.Dict) -> typing.NoReturn:
        schema: MarshmallowSchema = self._schema()
        failures = schema.validate(data=values)
        if not failures:
            return

        raise SchemaValuesError(errors=failures)

    def export(self) -> typing.NoReturn:
        raise Exception("Merged schemas are not exportable")
