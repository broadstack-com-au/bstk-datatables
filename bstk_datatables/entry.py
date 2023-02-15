import typing
from dataclasses import dataclass, field


@dataclass
class Entry:
    uuid: typing.AnyStr
    name: typing.AnyStr
    table_id: typing.AnyStr = field(default=None)
    references: typing.Dict[typing.AnyStr, typing.Any] = field(default=None)
    connector_references: typing.Dict[typing.AnyStr, typing.Any] = field(default=None)
    schemata: typing.List[typing.AnyStr] = field(default=None)
    values: typing.Dict[typing.AnyStr, typing.Any] = field(default=None)

    def __post_init__(self):
        if not self.references:
            self.references = {}
        if not self.connector_references:
            self.connector_references = {}
        if not self.schemata:
            self.schemata = []
        if not self.values:
            self.values = {}

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        return self.__dict__
