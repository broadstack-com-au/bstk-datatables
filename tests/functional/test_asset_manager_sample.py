from uuid import uuid4

import pytest

from bstk_datatables.entry import Entry
from bstk_datatables.schema import MergedSchema, Schema, SchemaField, SchemaValuesError
from bstk_datatables.table import Table


def test_simple_assetmanager_pattern():
    # Create a couple of schemas
    _hardware_schema = Schema(uuid=str(uuid4()), name="Hardware")
    assert _hardware_schema.code == "hardware"

    _name_field = SchemaField(
        name="Name", format={"type": "text", "default_value": "Name"}
    )
    _serial_field = SchemaField(name="Serial Number", format={"type": "text"})
    _type_field = SchemaField(
        name="Hardware type", format={"type": "text", "default_value": "Hardware"}
    )
    _hardware_schema.add_field(_name_field)
    _hardware_schema.add_field(_serial_field)
    _hardware_schema.add_field(_type_field)

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

    # This field will get ignored because already defined in the first schema (ignored during merge)
    _printer_type_field = SchemaField(
        name="Hardware type", format={"type": "text", "default_value": "printer"}
    )
    _printer_schema.add_field(_printer_type_field)

    # This field should come through with the default
    _hardware_subtype_field = SchemaField(
        name="Hardware subtype",
        format={"type": "text", "default_value": "printer", "readonly": True},
    )
    _printer_schema.add_field(_hardware_subtype_field)

    # Create a table that uses both schemas

    _printer_table = Table(uuid=str(uuid4()), name="Printers")
    _printer_table.add_schema(_hardware_schema)
    _printer_table.add_schema(_printer_schema.code)

    assert _hardware_schema.code in _printer_table.schemata
    assert _printer_schema.code in _printer_table.schemata

    # Create an entry and attach it to the table
    _printer_entry = Entry(uuid=str(uuid4()), name="Entry for printer")
    _printer_table.adopt_entry(_printer_entry)

    # Generate the merged schema so we can present it to the user for input
    _merged_table_schema = MergedSchema([_hardware_schema, _printer_schema])

    # Collect user data, keyed by the field code
    # @TODO - ?? specifically, how ??
    _user_data = {
        _name_field.code: "Hallway Printer",
        _serial_field.code: "XYZA10592",
        _format_field.code: "A0",
        _size_field.code: "Standalone",
    }

    # Validate the input
    with pytest.raises(SchemaValuesError) as excinfo:
        _merged_table_schema.check_values(_user_data)

    assert "paper_size" in excinfo.value.errors
    assert excinfo.value.errors["paper_size"] == [
        "Must be one of: " + ", ".join(_format_field.format.values) + "."
    ]

    # Prompt the user to correct their input for the invalid field
    # print(excinfo.value.errors)

    # Accept corrected user data
    _user_data[_format_field.code] = "A4"

    # Ensure the user data is now correct
    _merged_table_schema.check_values(_user_data)

    # Merge in our default values after validation (ensuring we don't trip over readonly fields)
    _user_data = _merged_table_schema.merge_defaults(_user_data)

    # Double check the schema would be unhappy about the readonly field having a value
    with pytest.raises(SchemaValuesError):
        _merged_table_schema.check_values(_user_data)

    # Make sure we've got our default value from the first hardware type entry
    assert _user_data.get(_type_field.code, None) == _type_field.format.default_value

    # Make sure we've got our default value from the second schema
    assert (
        _user_data.get(_hardware_subtype_field.code, None)
        == _hardware_subtype_field.format.default_value
    )

    # Make sure the name provided wasn't erased by the default value
    assert _user_data.get(_name_field.code, None) == "Hallway Printer"

    # Set the user data into the entry
    _printer_entry.values = _user_data

    # Grab the entry data so it can be saved
    _entry_for_saving = _printer_entry.export()
    assert _entry_for_saving["values"] == _user_data
