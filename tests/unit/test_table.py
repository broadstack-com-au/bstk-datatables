from uuid import uuid4

from bstk_datatables import export
from bstk_datatables.table import Table


def test_load_base_tablestruct():
    data = {
        "uuid": str(uuid4()),
        "name": "Data Table",
        "references": {"entity_uuid": str(uuid4())},
        "connectors": {"connector1": "connectorclass"},
        "schemata": ["table_schema"],
    }
    table = Table(**data)
    assert isinstance(table, Table)
    for field, val in data.items():
        assert getattr(table, field) == val


def test_table_export():
    data = {
        "uuid": str(uuid4()),
        "name": "Data Table",
        "references": {"entity_uuid": str(uuid4())},
        "connectors": {"connector1": "connectorclass"},
        "schemata": ["table_schema"],
    }
    table = Table(**data)
    exported = export(table)
    assert exported == data
