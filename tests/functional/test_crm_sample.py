import typing
from uuid import uuid4

import pytest

from bstk_datatables.entry import Entry
from bstk_datatables.schema import Schema, SchemaField
from bstk_datatables.table import Table


def test_complete_crm_pattern():
    # Create crm entity schema
    _entity_schema = Schema(uuid=str(uuid4()), name="CRM Entity")
    assert _entity_schema.code == "crm_entity"

    _entity_fields = {
        "Tags": {
            "type": "enum",
            "values": [
                "small",
                "large",
                "chase",
                "ignore",
            ],
        },
    }
    for fieldname, format in _entity_fields.items():
        _entity_schema.add_field(SchemaField(name=fieldname, format=format))

    # Create an add-on schema for organisations
    _org_schema = Schema(uuid=str(uuid4()), name="Organisations")
    assert _org_schema.code == "organisations"

    _org_fields = {"Address": {"type": "text"}, "Website": {"type": "url"}}
    for fieldname, format in _org_fields.items():
        _org_schema.add_field(SchemaField(name=fieldname, format=format))

    # Create a table for organisations
    _org_table = Table(uuid=str(uuid4()), name="Organisations")
    _org_table.add_schema(_entity_schema)
    _org_table.add_schema(_org_schema)

    # Create crm event schema
    _event_schema = Schema(uuid=str(uuid4()), name="CRM Event")
    _event_fields = {
        "Type": {
            "type": "enum",
            "values": [
                "call",
                "meeting",
                "task",
                "deadline",
                "email",
                "catchup",
                "change",
            ],
        },
        "Content": {"type": "text"},
        "Action": {"type": "datetime"},
        "Duration": {"type": "number"},
        "Complete": {"type": "bool"},
        "Linked Organisation": {"type": "connector"},
        "Linked Contact": {"type": "connector"},
    }
    for fieldname, format in _event_fields.items():
        _event_schema.add_field(SchemaField(name=fieldname, format=format))

    # Create a table for events
    _event_table = Table(uuid=str(uuid4()), name="Events")
    _event_table.add_schema(_event_schema)

    # Create some organisations and add them to the table
    _org_one = Entry(
        uuid=str(uuid4()),
        name="Organisation One",
        values={"address": "1 Organisation Street, Somewhere", "tags": "large"},
    )
    _org_table.adopt_entry(_org_one)

    _org_two = Entry(
        uuid=str(uuid4()),
        name="Organisation Two",
        values={"address": "Unit 1, 52 Country Street, Somewhere", "tags": "small"},
    )
    _org_table.adopt_entry(_org_two)

    # Create an add-on schema for contacts
    _contact_schema = Schema(uuid=str(uuid4()), name="Contacts")
    assert _contact_schema.code == "contacts"

    _contact_fields = {
        "Firstname": {"type": "text"},
        "Lastname": {"type": "text"},
        "Email": {"type": "email"},
        "Phone": {"type": "phone"},
    }
    for fieldname, format in _contact_fields.items():
        _contact_schema.add_field(SchemaField(name=fieldname, format=format))

    # Create a table for contacts
    _contact_table = Table(uuid=str(uuid4()), name="Contacts")
    _contact_table.add_schema(_entity_schema)
    _contact_table.add_schema(_contact_schema)

    # Create some contacts
    _contact_one = Entry(
        uuid=str(uuid4()),
        name="Contact One",
        values={
            "firstname": "Contact",
            "lastname": "One",
            "email": "contact1@example.com",
        },
    )
    _contact_table.adopt_entry(_contact_one)

    _contact_two = Entry(
        uuid=str(uuid4()),
        name="Contact two",
        values={
            "firstname": "Contact",
            "lastname": "two",
            "email": "contact2@example.com",
        },
    )
    _contact_table.adopt_entry(_contact_two)

    # Organise our data
    _contacts: typing.List[Entry] = [_contact_one, _contact_two]
    _organisations: typing.List[Entry] = [_org_one, _org_two]

    # link some contacts to org one
    _org_one.link_to(_contact_one)
    _org_one.link_to(_contact_two)

    # Get a list of contacts for each organisation - pretend we are querying a database where the connector_references are indexed..
    def _count_linked_entries(linker: Entry, entries: typing.List[Entry]) -> int:
        return len([_entry for _entry in entries if _entry.is_linked_to(linker)])

    assert _count_linked_entries(_org_one, _contacts) == 2
    assert _count_linked_entries(_org_two, _contacts) == 0

    _org_one.unlink_from(_contact_one)
    assert _count_linked_entries(_org_one, _contacts) == 1

    _org_two.link_to(_contact_two)
    assert _count_linked_entries(_org_two, _contacts) == 1
    assert _count_linked_entries(_org_one, _contacts) == 0

    _org_one.link_to(_org_two)
    assert _count_linked_entries(_org_one, _organisations) == 1

    # Push an event into the event table
    _event = Entry(
        uuid=str(uuid4()),
        name="New Event",
        values={
            "type": "call",
            "content": "Call with Joe",
            "action": "2023-12-01T16:00:00+1000",
            "duration": "60",
            "complete": "false",
            "linked_organisation": _org_one.uuid,
            "linked_contact": _contact_one.uuid,
        },
    )
    _event_table.adopt_entry(_event)
    _event_schema.process_entry(_event)
    assert "linked_organisation" not in _event.values
    assert "linked_contact" not in _event.values

    assert "linked_organisation" in _event.connector_references
    assert "linked_contact" in _event.connector_references
