from uuid import uuid4

from bstk_datatables.entry import Entry
from bstk_datatables.merge import MergedSchema
from bstk_datatables.table import Table


def test_table_adopt():
    table_data = {
        "uuid": str(uuid4()),
        "name": "Data Table",
        "references": {"entity_uuid": str(uuid4())},
        "connectors": {"connector1": "connectorclass"},
        "schemata": ["table_schema"],
    }
    table = Table(**table_data)

    entry_data = {
        "uuid": str(uuid4()),
        "table_id": str(uuid4()),
        "name": "Data Entry",
        "references": {"entity_uuid": str(uuid4())},
        "connector_references": {"connector1": "connector_ref"},
        "schemata": ["base"],
        "values": {"base/value1": "XG230"},
    }
    entry = Entry(**entry_data)

    table.adopt_entry(entry)
    assert entry.table_id == table.uuid
    assert "base" in entry.schemata
    assert set(set(table.schemata) & set(entry.schemata)) == set(["table_schema"])


def test_table_process_entry():
    table_data = {
        "uuid": str(uuid4()),
        "name": "Data Table",
        "references": {"entity_uuid": str(uuid4())},
        "connectors": {"connector1": "connectorclass"},
        "schemata": ["table_schema"],
    }
    table = Table(**table_data)

    entry_data = {
        "uuid": str(uuid4()),
        "table_id": None,
        "name": "Data Entry",
        "references": {"entity_uuid": str(uuid4())},
        "connector_references": {"connector1": "connector_ref"},
        "schemata": ["base"],
        "values": {"entry_type": "Test Entry", "value1": "XG230"},
    }
    entry = Entry(**entry_data)
    table.adopt_entry(entry)

    _schemas = {
        "table_schema": {
            "uuid": str(uuid4()),
            "references": {"entity_uuid": str(uuid4())},
            "name": "Table Schema",
            "code": "table_schema",
            "fields": [
                {
                    "name": "entry_type",
                    "format": {
                        "type": "text",
                    },
                },
            ],
        },
        "base": {
            "uuid": str(uuid4()),
            "references": {"entity_uuid": str(uuid4())},
            "name": "Base Schema",
            "code": "base",
            "fields": [
                {
                    "name": "value1",
                    "format": {
                        "type": "text",
                    },
                },
            ],
        },
    }

    _schemalist = []
    for _schema in entry.schemata:
        _schemalist.append(_schemas[_schema])

    _merged_schema = MergedSchema(schemata=_schemalist)
    _merged_schema.process_values(entry.values)
