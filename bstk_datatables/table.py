import typing
from dataclasses import dataclass


@dataclass
class Table:
    uuid: typing.AnyStr
    name: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    connectors: typing.Dict[typing.AnyStr, typing.Any]

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        return self.__dict__
