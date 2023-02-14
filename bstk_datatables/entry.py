import typing
from dataclasses import dataclass


@dataclass
class Entry:
    uuid: typing.AnyStr
    table_id: typing.AnyStr
    name: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    connector_references: typing.Dict[typing.AnyStr, typing.Any]
    schemata: typing.List[typing.AnyStr]
    values: typing.Dict[typing.AnyStr, typing.Any]

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        return self.__dict__
