import typing
from dataclasses import dataclass

from .entry import Entry


@dataclass
class Table:
    uuid: typing.AnyStr
    name: typing.AnyStr
    references: typing.Dict[typing.AnyStr, typing.Any]
    connectors: typing.Dict[typing.AnyStr, typing.Any]
    schemata: typing.List[typing.AnyStr]

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        return self.__dict__

    def adopt(self, entry: Entry) -> Entry:
        entry.table_id = self.uuid
        entry.schemata = list(dict.fromkeys(self.schemata + entry.schemata))
        return entry
