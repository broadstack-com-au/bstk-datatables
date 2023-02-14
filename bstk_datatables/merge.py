import typing
from dataclasses import dataclass, field

from marshmallow import Schema as MarshmallowSchema

from .schema import Schema, SchemaField, SchemaValuesError


@dataclass
class MergedSchema:
    schemata: typing.List[typing.Union[typing.Dict, Schema]]
    _schemata: typing.List[typing.AnyStr] = field(init=False, default=None)
    fields: typing.List[SchemaField] = field(init=False, default=None)
    _fields: typing.List[typing.AnyStr] = field(init=False, default=None)
    _schema: MarshmallowSchema = field(init=False, default=None)

    def __post_init__(self):
        if len(self.schemata) < 1:
            return

        self._schemata = []
        self.fields = []
        self._fields = []
        for schema in self.schemata:
            if isinstance(schema, Schema):
                self._add_field(_field for _field in schema.fields)
                self._schemata.append(schema.name)

            if "fields" in schema:
                _schemaname = f"schema_{len(self._schemata)}"
                if "name" in schema:
                    _schemaname = schema["name"]
                self._schemata.append(_schemaname)
                for dictfield in schema["fields"]:
                    self._add_field(SchemaField(**dictfield))

        self._schema = self._build_schema()

    def _add_field(self, new_field: SchemaField) -> None:
        if new_field.name in self._fields:
            return
        self._fields.append(new_field.name)
        self.fields.append(new_field)

    def _build_schema(self) -> MarshmallowSchema:
        schema_struct = {}
        for schemafield in self.fields:
            schema_struct[schemafield.name] = schemafield.format._field

        return MarshmallowSchema.from_dict(
            schema_struct, name="Merged schema: " + ", ".join(self._schemata)
        )

    def process_values(self, values: typing.Dict) -> typing.NoReturn:
        schema: MarshmallowSchema = self._schema()
        failures = schema.validate(data=values)
        if not failures:
            return

        raise SchemaValuesError(errors=failures)
