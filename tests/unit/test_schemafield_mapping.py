from marshmallow.fields import (AwareDateTime, Boolean, Email, IPInterface,
                                Number, String, Url)

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


def test_schemafield_blob():
    field = SchemaField(
        **{
            "name": "text_value",
            "format": {
                "type": "blob",
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


def test_schemafield_ipinterface():
    field = SchemaField(**{"name": "ip_value", "format": {"type": "ip"}})
    assert isinstance(field.format._field, IPInterface)


def test_schemafield_url():
    field = SchemaField(**{"name": "ip_value", "format": {"type": "url"}})
    assert isinstance(field.format._field, Url)


def test_schemafield_email():
    field = SchemaField(**{"name": "ip_value", "format": {"type": "email"}})
    assert isinstance(field.format._field, Email)
