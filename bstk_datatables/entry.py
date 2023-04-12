from __future__ import annotations

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

    def link_to(self, entry: Entry) -> None:
        if not self.table_id:
            raise ValueError("Cannot link entries that are not attached to a table")
        if not self.uuid:
            raise ValueError(
                "Cannot link entries if the linker does not have a uuid set"
            )

        entry.connector_references[self.table_id] = self.uuid

    def unlink_from(self, entry: Entry) -> None:
        if not self.table_id:
            raise ValueError(
                "Cannot unlink entries that have not been attached to a table"
            )

        if not self.uuid:
            raise ValueError(
                "Cannot unlink entries if the unlinker does not have a uuid set"
            )

        if self.table_id not in entry.connector_references:
            return

        if entry.connector_references[self.table_id] != self.uuid:
            return

        del entry.connector_references[self.table_id]

    def is_linked_to(self, entry: Entry) -> bool:
        if not entry.table_id:
            return False
        if not self.connector_references:
            return False
        if entry.table_id not in self.connector_references:
            return False
        if not self.connector_references[entry.table_id]:
            return False
        if self.connector_references[entry.table_id] != entry.uuid:
            return False

        return True
