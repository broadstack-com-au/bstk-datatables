from __future__ import annotations

import typing
from dataclasses import dataclass, field

from . import name_to_code
from .entry import Entry
from .schema import Schema


@dataclass
class Table:
    uuid: typing.AnyStr
    name: typing.AnyStr
    code: typing.Optional[typing.AnyStr] = field(default=None)
    references: typing.Dict[typing.AnyStr, typing.Any] = field(default=None)
    connectors: typing.Dict[typing.AnyStr, typing.Any] = field(default=None)
    schemata: typing.List[typing.AnyStr] = field(default=None)

    def __post_init__(self):
        if not self.code:
            self.code = name_to_code(self.name)

        if not self.references:
            self.references = {}
        if not self.connectors:
            self.connectors = {}
        if not self.schemata:
            self.schemata = []

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        return self.__dict__

    def add_schema(self, schema: typing.Union[typing.AnyStr, Schema]) -> None:
        _schema = None
        if isinstance(schema, Schema):
            _schema = schema.code
        if isinstance(schema, str):
            _schema = schema

        if not _schema:
            raise ValueError("Invalid value for `schema`")

        if _schema in self.schemata:
            return

        self.schemata.append(_schema)

    def adopt_entry(self, entry: Entry) -> Entry:
        if entry.table_id != self.uuid:
            entry.table_id = self.uuid

        entry.schemata = list(dict.fromkeys(self.schemata + entry.schemata))
        return entry
