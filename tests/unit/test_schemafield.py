import marshmallow

from bstk_datatables.schema import SchemaField


def test_schemafield_thin():
    field_data = {
        "name": "text_value",
        "code": "text_value",
        "format": {
            "type": "text",
        },
    }
    field = SchemaField(**field_data)
    assert field.export() == field_data
    assert isinstance(field.format._field, marshmallow.fields.Field)


def test_schemafield_wide():
    field_data = {
        "name": "localenum_value",
        "code": "localenum_value",
        "format": {
            "type": "enum",
            "values": [
                "Local Enum Value 1",
                "Local Enum Value 2",
                "Local Enum Value 3",
            ],
            "required": True,
            "many": True,
            "readonly": True,
            "markup": {"class": "class_1", "style": "max-width: 50%"},
        },
    }

    field = SchemaField(**field_data)
    assert field.export() == field_data
    assert isinstance(field.format._field, marshmallow.fields.Field)
