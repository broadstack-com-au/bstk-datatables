from marshmallow.fields import AwareDateTime, Boolean, Number, String

from bstk_datatables.schema import SchemaField


def test_schemafield_text():
    field = SchemaField(
        **{
            "name": "text_value",
            "format": {
                "type": "text",
            },
        }
    )
    assert isinstance(field.format._field, String)


def test_schemafield_number():
    field = SchemaField(
        **{
            "name": "number_value",
            "format": {
                "type": "number",
            },
        }
    )
    assert isinstance(field.format._field, Number)


def test_schemafield_bool():
    field = SchemaField(
        **{
            "name": "boolean_value",
            "format": {
                "type": "bool",
            },
        }
    )
    assert isinstance(field.format._field, Boolean)


def test_schemafield_datetime():
    field = SchemaField(
        **{
            "name": "datetime_value",
            "format": {
                "type": "datetime",
            },
        }
    )
    assert isinstance(field.format._field, AwareDateTime)
