import typing
from dataclasses import dataclass, field

from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields as marshmallow_fields

from . import SCHEMAFIELD_MAP
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
    fields: typing.List["SchemaField"]
    _schema: MarshmallowSchema = field(init=False, default=None)

    def __post_init__(self):
        self.fields = [SchemaField(**field) for field in self.fields]
        self._schema = self._build_schema()

    def add_field(self, field_data: typing.Dict[typing.AnyStr, typing.Any]):
        self.fields.append([SchemaField(**field_data)])
        self._schema = self._build_schema()

    def _build_schema(self) -> MarshmallowSchema:
        schema_struct = {}
        for schemafield in self.fields:
            schema_struct[schemafield.name] = schemafield.format._field

        return MarshmallowSchema.from_dict(schema_struct, name=self.name)

    def process_values(self, values: typing.Dict) -> typing.NoReturn:
        schema: MarshmallowSchema = self._schema()
        failures = schema.validate(data=values)
        if not failures:
            return

        raise SchemaValuesError(errors=failures)


@dataclass
class SchemaField:
    name: typing.AnyStr
    format: "SchemaFieldFormat"
    _value: typing.Any = field(init=False, default=None)

    def __post_init__(self):
        self.format = SchemaFieldFormat(**self.format)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


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
        field_params = {}

        if self.type == "enum":
            if self.values:
                field_params["enum"] = PyEnum("enum", self.values)
            elif self.lookup and isinstance(self.lookup, Enum):
                field_params["enum"] = self.lookup.values
            else:
                return

        self._field = self._get_mapped_fieldclass(self.type)(**field_params)
