import typing
from dataclasses import dataclass


@dataclass
class Entry:
    uuid: typing.AnyStr
    name: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    connector_references: typing.Dict[typing.AnyStr, typing.Any]
    schema: typing.List[typing.AnyStr]
    values: typing.Dict[typing.AnyStr, typing.Any]
