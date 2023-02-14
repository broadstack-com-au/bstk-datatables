import typing
from enum import Enum as PyEnum
from dataclasses import dataclass


@dataclass
class Enum:
    uuid: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    code: typing.AnyStr
    name: typing.AnyStr
    values: PyEnum

    def __post_init__(self):
        vals = [val.upper() for val in self.values]
        self.values = PyEnum(self.name, vals)
