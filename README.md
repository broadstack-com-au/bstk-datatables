# Datatables - structured data library based on schemas

[homepage](https://github.com/broadstack-com-au/datatables)

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

## Overview & Usage

### Schema

Schema models are;

* `Schema`: A collection of fields and references that make up a partial or complete entry
* `SchemaField`: A basic instruction container representing a single value
* `SchemaFieldFormat`: The specific instructions for how the field should be collected, represented, formatted and stored
* `SchemaValuesError`: The only type of exception raised during schema validation

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

## Extras

### MergedSchema

Tables and Entries support more than a single schema reference.  
`MergedSchema` exists to facilitate mutli-schema validation and field ordering.

Provide `Dict[Schema.Code: Schema]` as `schemata` when initialising a `MergedSchema` and it will:

1. Process the schema in order
1. De-dupe fields with the same code (first schema wins)
1. Be ready to validate entries with the provided schemaset

### Enum

Enum are used within schemas as de-duped lookups. Multiple schema fields can use the same Enum for shaping values.  

Usage:

1. Provide an `Enum.code` as a `lookup` instead of a `values` list when supplying `SchemaFieldFormat` to a schemafield.
1. Provide the `Enum` to `Schema.attach_lookup` on a compiled `Schema` or `MergedSchema`.
