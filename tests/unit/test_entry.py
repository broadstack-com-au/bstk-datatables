from uuid import uuid4

from bstk_datatables.entry import Entry


def test_load_base_entrystruct():
    data = {
        "uuid": str(uuid4()),
        "table_id": str(uuid4()),
        "name": "Data Entry",
        "references": {"entity_uuid": str(uuid4())},
        "connector_references": {"connector1": "connector_ref"},
        "schemata": ["base"],
        "values": {"base/value1": "XG230"},
    }
    entry = Entry(**data)
    assert isinstance(entry, Entry)
    for field, val in data.items():
        assert getattr(entry, field) == val
