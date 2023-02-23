# Datatables - structured data library based on schemas

[homepage](https://github.com/broadstack-com-au/bstk-datatables)

## Dev

1. `poetry install`
1. `poetry shell`  
-- Make changes --
1. `poetry run pytest`
1. `poetry run black bstk_datatables`
1. `poetry run flake8 bstk_datatables`  
-- Commit & Push --

## Install

`pip install bstk-datatables`

## Overview

Datatables act as an intermediary between [Marshmallow structures](https://marshmallow.readthedocs.io/en/stable/) and user defined data storage structures.  
It is designed to provide "just enough" sidechannel structure to facilitate building a dynamic schema, (and connecting with "other" interfaces), without losing the advantages afforded by static Marshmallow schemas.

### Schema

Schema models are;

* `Schema`: A collection of fields and references that make up a partial or complete entry
* `SchemaField`: A basic instruction container representing a single value
* `SchemaFieldFormat`: The specific instructions for how the field should be collected, represented, formatted and stored
* `SchemaValuesError`: The only type of exception raised during schema validation

These schemas and fields are mapped to equivalent [Marshmallow structures](https://marshmallow.readthedocs.io/en/stable/) which provide the entry value validation mechanisms.. ref: `Schema.process_values()`

### Entry

An `Entry` is a collection of field values, references data, connector references and schema links.

* `.schemata` is a list of `Schema.code`'s
* `.table_id` is a link back to a `Table.uuid`
* `.references` and `.connector_references` are unrestricted containers. Two containers are provided to seperate "core" references from "free-form" references.
* `.values` is a dict of `Field.code` => `value` that conform to the listed schemata

### Table

A `Table` corrals one or more `Entry` and shapes them towards one or more `Schema`.

* `.schemata` is a list of `Schema.code`'s that all entries _must_ inherit
* `.references` and `.connectors` are unrestricted containers. Two containers are provided to seperate "core" references from "free-form" references (and allows correlation with table entries).

### Marshalling and Persistence

All core classes (and `Enum`) expose an `export` method which return a dict.  
The result of an `export()` can be unpacked and provided to its constructor.  

```python

def test_entry_export():
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
    exported = export(entry)
    assert exported == data

```

The simplest way to handle data persistence is to encapsulate class instanciation and the `export` method of the relevant class into an ORM or ODM framework.  
`MergeSchema` do not provide an export mechanism because they are not first-class citizens and are designed to work with established `Schema` structures.

[This test provides an example of how to implement persistence with flat files](./tests/functional/test_persistence_documents.py#106).

## Extras

### MergedSchema

Tables and Entries support more than a single schema reference.  
`MergedSchema` exists to facilitate mutli-schema validation and field ordering.

Provide `Dict[Schema.Code: Schema]` as `schemata` when initialising a `MergedSchema` and it will:

1. Process the schema in order
1. De-dupe fields with the same code (If a later schema includes a field with the same code as a previously loaded schema - that field will be skipped)
1. Provide a validation mechanism for entries

### Enum

Enum are used within schemas as de-duped lookups. Multiple schema fields can use the same Enum for shaping values.  

Usage:

1. Provide an `Enum.code` as a `lookup` instead of a `values` list when supplying `SchemaFieldFormat` to a schemafield.
1. Provide the instanciated `Enum` to `Schema.attach_lookup` on a compiled `Schema` or `MergedSchema`.  

__or__

1. Provide an instanciated `Enum` as a `lookup` instead of a `values` list when supplying `SchemaFieldFormat` to a schemafield.
