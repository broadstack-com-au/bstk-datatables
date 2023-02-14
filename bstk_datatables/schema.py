import typing
from dataclasses import dataclass


@dataclass
class Schema:
    uuid: typing.AnyStr
    name: typing.AnyStr
    code: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    fields: typing.List["SchemaField"]

    def __post_init__(self):
        self.fields = [SchemaField(**field) for field in self.fields]


@dataclass
class SchemaField:
    name: typing.AnyStr
    format: "SchemaFieldFormat"

    def __post_init__(self):
        self.format = SchemaFieldFormat(**self.format)


@dataclass
class SchemaFieldFormat:
    type: typing.Optional[typing.AnyStr]
    values: typing.Optional[typing.Any] = None
    lookup: typing.Optional[typing.Any] = None
