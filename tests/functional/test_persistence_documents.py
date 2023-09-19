import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest

import bstk_datatables
from bstk_datatables.entry import Entry
from bstk_datatables.schema import MergedSchema, Schema, SchemaField, SchemaValuesError
from bstk_datatables.table import Table

TEMPDIR = TemporaryDirectory()


@pytest.fixture(scope="session", autouse=True)
def pytest_sessionstart():
    test_data = []

    # Hardware Schema
    _hardware_schema = Schema(uuid=str(uuid4()), name="Hardware")

    _name_field = SchemaField(name="Name", format={"type": "text", "required": True})
    _serial_field = SchemaField(name="Serial Number", format={"type": "text"})
    _hardware_schema.add_field(_name_field)
    _hardware_schema.add_field(_serial_field)

    _saveable_hardware_schema = bstk_datatables.export(_hardware_schema)

    test_data.append(
        {
            "type": "schema",
            "code": _saveable_hardware_schema["code"],
            "body": _saveable_hardware_schema,
        }
    )

    # Printer Schema
    _printer_schema = Schema(uuid=str(uuid4()), name="Printers and print equipment")
    assert _printer_schema.code == "printers_and_print_equipment"

    _format_field = SchemaField(
        name="Paper Size", format={"type": "enum", "values": ["A5", "A4", "A3"]}
    )
    _size_field = SchemaField(
        name="Physical size",
        format={
            "type": "enum",
            "values": ["Portable", "Desktop", "Standalone", "Pallet"],
        },
    )
    _printer_schema.add_field(_format_field)
    _printer_schema.add_field(_size_field)

    _saveable_printer_schema = bstk_datatables.export(_printer_schema)
    test_data.append(
        {
            "type": "schema",
            "code": _saveable_printer_schema["code"],
            "body": _saveable_printer_schema,
        }
    )

    _printer_table = Table(uuid=str(uuid4()), name="Printers")
    _printer_table.add_schema(_hardware_schema)
    _printer_table.add_schema(_printer_schema.code)
    test_data.append(
        {
            "type": "table",
            "code": "printer",
            "body": bstk_datatables.export(_printer_table),
        }
    )

    _printer_entry = Entry(uuid=str(uuid4()), name="Entry for printer")
    _printer_table.adopt_entry(_printer_entry)
    test_data.append(
        {
            "type": "entry",
            "code": "printer",
            "body": bstk_datatables.export(_printer_entry),
        }
    )

    tmp_path = Path(TEMPDIR.name)

    for _data in test_data:
        with open(
            tmp_path.joinpath(f"{_data['type']}.{_data['code']}.json"), "w"
        ) as fp:
            json.dump(_data["body"], fp)


def pytest_sessionfinish(session, exitstatus):
    # remove the cached images
    TEMPDIR.cleanup()


def load_document(type, code):
    tmp_path = Path(TEMPDIR.name)
    with open(tmp_path.joinpath(f"{type}.{code}.json"), "r") as fp:
        return json.load(fp)


def test_process_data_from_documents(request):
    # load the printer table
    _printer_table = Table(**load_document("table", "printer"))

    # load the schemas for the printer table
    _loaded_schemas = []
    for _schema in _printer_table.schemata:
        _loaded_schemas.append(Schema(**load_document("schema", _schema)))

    # Load the entry being modified
    _printer_entry = Entry(**load_document("entry", "printer"))
    assert _printer_entry.table_id == _printer_table.uuid

    # Generate the merged schema so we can present it to the user for input
    _merged_table_schema = MergedSchema(_loaded_schemas)

    # Collect user data, keyed by the field code
    # @TODO - ?? specifically, how ??
    _user_data = {
        "serial_number": "XXXX10592",
        "paper_size": "A0",
        "physical_size": "Standalone",
    }

    # Validate the input
    with pytest.raises(SchemaValuesError) as excinfo:
        _merged_table_schema.check_values(_user_data)

    assert "name" in excinfo.value.errors
    assert excinfo.value.errors["name"] == ["Missing data for required field."]

    assert "paper_size" in excinfo.value.errors
    assert excinfo.value.errors["paper_size"] == [
        "Must be one of: " + ", ".join(["A5", "A4", "A3"]) + "."
    ]

    # Accept corrected user data
    _user_data["paper_size"] = "A4"
    _user_data["name"] = "Asset name"

    # Ensure the user data is now correct
    _merged_table_schema.check_values(_user_data)

    # Set the user data into the entry
    _printer_entry.values = _user_data

    # Grab the entry data so it can be saved
    _entry_for_saving = _printer_entry.export()
    assert _entry_for_saving["values"] == _user_data
