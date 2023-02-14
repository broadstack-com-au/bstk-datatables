import typing
from dataclasses import dataclass


@dataclass
class Enum:
    uuid: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    code: typing.AnyStr
    name: typing.AnyStr
    values: typing.List[typing.AnyStr]
