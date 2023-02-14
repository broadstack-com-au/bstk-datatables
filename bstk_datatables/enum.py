import copy
import typing
from dataclasses import dataclass
from enum import Enum as PyEnum


@dataclass
class Enum:
    uuid: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    code: typing.AnyStr
    name: typing.AnyStr
    values: PyEnum

    def __post_init__(self):
        vals = [val for val in self.values]
        self.values = PyEnum(self.name, vals)

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        rtn = copy.copy(self.__dict__)
        rtn["values"] = [v.name for v in self.values]
        return rtn
