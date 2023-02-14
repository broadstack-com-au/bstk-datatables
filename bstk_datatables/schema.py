import typing
from dataclasses import dataclass


@dataclass
class Schema:
    uuid: typing.AnyStr
    name: typing.AnyStr
    code: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    fields: typing.List[typing.Any]
