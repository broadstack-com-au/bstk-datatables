from uuid import uuid4

import pytest

import bstk_datatables
from bstk_datatables.entry import Entry
from bstk_datatables.merge import MergedSchema
from bstk_datatables.schema import Schema, SchemaField, SchemaValuesError
from bstk_datatables.table import Table


def test_simple_usage_pattern():
    # Create a couple of schemas
    _hardware_schema = Schema(uuid=str(uuid4()), name="Hardware")
    assert _hardware_schema.code == "hardware"

    _name_field = SchemaField(name="Name", format={"type": "text"})
    _serial_field = SchemaField(name="Serial Number", format={"type": "text"})
    _hardware_schema.add_field(_name_field)
    _hardware_schema.add_field(_serial_field)

    _saveable_hardware_schema = bstk_datatables.export(_hardware_schema)

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

    # Create a table that uses both schemas

    _printer_table = Table(uuid=str(uuid4()), name="Printers")
    _printer_table.add_schema(_hardware_schema)
    _printer_table.add_schema(_printer_schema.code)

    assert _hardware_schema.code in _printer_table.schemata
    assert _printer_schema.code in _printer_table.schemata

    # Create an entry and attach it to the table
    _printer_entry = Entry(uuid=str(uuid4()), name="Entry for printer")
    _printer_table.adopt(_printer_entry)

    # Collect user data, keyed by the field code
    # @TODO - ?? how ??
    _user_data = {
        _name_field.code: "Hallway Printer",
        _serial_field.code: "XXXX10592",
        _format_field.code: "A0",
        _size_field.code: "Standalone",
    }

    # Generate the merged schema so we can validate the user input
    _merged_table_schema = MergedSchema([_hardware_schema, _printer_schema])

    # Validate the input
    with pytest.raises(SchemaValuesError) as excinfo:
        _merged_table_schema.process_values(_user_data)

    assert "paper_size" in excinfo.value.errors
    assert excinfo.value.errors["paper_size"] == [
        "Must be one of: " + ", ".join(_format_field.format.values) + "."
    ]
    # Prompt the user to correct their input for the invalid field
    print(excinfo.value.errors)

    # Accept corrected user data
    _user_data[_format_field.code] = "A4"

    # Ensure the user data is now correct
    _merged_table_schema.process_values(_user_data)

    # Set the user data into the entry
    _printer_entry.values = _user_data

    # Grab the entry data so it can be saved
    print(_printer_entry.export())
