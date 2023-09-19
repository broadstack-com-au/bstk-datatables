from __future__ import annotations

import copy
import typing
import warnings
from dataclasses import dataclass, field

from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields as marshmallow_fields

from . import (
    SCHEMAFIELD_EXTATTR,
    SCHEMAFIELD_MAP,
    RegexpValidator,
    name_to_code,
    re,
    schema_to_marshmallow,
)
from .entry import Entry
from .enum import Enum, PyEnum


class NestedSchemaField(marshmallow_fields.Field):
    """
    A little helper class to use if you're nesting a Schema as a field within another marshmallow schema.
    """

    def _serialize(
        self,
        value: typing.Any,
        attr: typing.Union[str, None],
        obj: typing.Any,
        **kwargs,
    ):
        if isinstance(value, Schema):
            return value.export()
        return value


class SchemaValuesError(Exception):
    errors: typing.Dict[typing.AnyStr, typing.List[typing.AnyStr]]

    def __init__(
        self,
        *args: object,
        errors: typing.Dict[typing.AnyStr, typing.List[typing.AnyStr]],
    ) -> None:
        self.errors = errors
        super().__init__(*args)


class AbstractSchema:
    fields: typing.Optional[
        typing.List[typing.Union[SchemaField, typing.Dict[typing.AnyStr, typing.Any]]]
    ]
    _field_list: typing.List[typing.AnyStr]
    _schema: MarshmallowSchema
    _missing_lookups: typing.Dict[typing.AnyStr, typing.List[SchemaFieldFormat]]

    def set_fields(self, schema_fields: typing.List[SchemaField]):
        self._field_list = []
        self.fields = []
        for schema_field in schema_fields:
            self.add_field(schema_field)

    def attach_lookup(self, lookup: Enum) -> None:
        if lookup.code not in self._missing_lookups:
            raise ValueError(f"Invalid lookup reference `{lookup.code}")
        for _missing_lookup in self._missing_lookups[lookup.code]:
            _missing_lookup.attach_lookup(lookup)
        del self._missing_lookups[lookup.code]

        if len(self._missing_lookups) < 1:
            self._schema = schema_to_marshmallow(self)

    def process_values(self, values: typing.Dict) -> None:
        warnings.warn(
            "`process_values` is deprecated. Use `check_values` for compatibility. "
            "`process_entry` should be used instead for extended entry processing and validation. ",
            DeprecationWarning,
            stacklevel=2,
        )
        self.check_values(values)

    def check_values(self, values: typing.Dict) -> None:
        if not self.is_complete() and not self.build():
            raise ValueError("Schema is incomplete")

        _schema: MarshmallowSchema = self._schema()
        failures = _schema.validate(data=values)
        if not failures:
            return

        raise SchemaValuesError(errors=failures)

    def get_defaults(self) -> typing.Dict:
        _schema: MarshmallowSchema = self._schema()
        return _schema.dump({})

    def merge_defaults(self, values: typing.Dict) -> typing.Dict:
        _defaults = self.get_defaults()
        return {**_defaults, **values}

    def is_complete(self) -> bool:
        if len(self.fields) < 1:
            return False
        if len(self._missing_lookups) > 0:
            return False
        if not self._schema:
            return False

        if not isinstance(self._schema, MarshmallowSchema) and not issubclass(
            self._schema, MarshmallowSchema
        ):
            return False

        return True

    def build(self) -> bool:
        if len(self.fields) < 1:
            return False
        if len(self._missing_lookups) > 0:
            return False

        self._schema = schema_to_marshmallow(self)
        return True

    def process_entry(self, entry: Entry) -> Entry:
        if not self.is_complete() and not self.build():
            raise ValueError("Schema is incomplete")

        _connector_fields: typing.List[str] = []
        for _field in self.fields:
            if _field.format.type != "connector":
                continue
            if _field.code not in entry.values:
                continue
            _connector_fields.append(_field.code)

        _schema: MarshmallowSchema = self._schema(only=_connector_fields)
        _connector_data: typing.Dict = _schema.dump(entry.values)
        for _k, _v in _connector_data.items():
            entry.connector_references[_k] = _v
            del entry.values[_k]

        return entry


@dataclass
class Schema(AbstractSchema):
    uuid: typing.AnyStr
    name: typing.AnyStr
    code: typing.Optional[typing.AnyStr] = field(default=None)
    references: typing.Optional[typing.Dict[typing.AnyStr, typing.Any]] = field(
        default=None
    )
    fields: typing.Optional[
        typing.List[typing.Union[SchemaField, typing.Dict[typing.AnyStr, typing.Any]]]
    ] = field(default=None)
    _field_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    _schema: MarshmallowSchema = field(init=False, default=None)
    _missing_lookups: typing.Dict[
        typing.AnyStr, typing.List[SchemaFieldFormat]
    ] = field(init=False, default=None)

    def __post_init__(self):
        self._missing_lookups = {}
        self._field_list = []

        if not self.code:
            self.code = name_to_code(self.name)

        if not self.fields:
            self.fields = []
            return

        _fields = copy.deepcopy(self.fields)
        self.fields = []
        for _field_data in _fields:
            if isinstance(_field_data, SchemaField):
                self.add_field(_field_data)
            else:
                self.add_field(SchemaField(**_field_data))

        for _field in self.fields:
            if _field.format._missing_lookup:
                if _field.format.lookup not in self._missing_lookups:
                    self._missing_lookups[_field.format.lookup] = []
                self._missing_lookups[_field.format.lookup].append(_field.format)

    def add_field(self, schema_field: SchemaField) -> None:
        if schema_field.code in self._field_list:
            raise ValueError(f"Duplicate field name `{schema_field.name}`")
        self._field_list.append(schema_field.code)
        self.fields.append(schema_field)

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        _fields = ["uuid", "name", "code", "references"]
        rtn = {}
        for _exportfield in _fields:
            rtn[_exportfield] = self.__dict__[_exportfield]
        rtn["fields"] = [_field.export() for _field in self.fields]
        return rtn


@dataclass
class MergedSchema(AbstractSchema):
    schemata: typing.List[typing.Union[typing.Dict[typing.AnyStr, typing.Any], Schema]]
    name: typing.AnyStr = field(default=None)
    _schema_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    fields: typing.Optional[
        typing.List[typing.Union[SchemaField, typing.Dict[typing.AnyStr, typing.Any]]]
    ] = field(default=None)
    _field_list: typing.List[typing.AnyStr] = field(init=False, default=None)
    _schema: MarshmallowSchema = field(init=False, default=None)
    _missing_lookups: typing.Dict[
        typing.AnyStr, typing.List[SchemaFieldFormat]
    ] = field(init=False, default=None)

    def __post_init__(self):
        self._missing_lookups = {}
        self._schema_list = []
        self.fields = []
        self._field_list = []

        if len(self.schemata) < 1:
            return

        self.load_schemas()

        self.process_fields()

        if not self.name:
            self.name = f"Merged schema: {', '.join(self._schema_list)}"

        if not self._missing_lookups:
            self._schema = schema_to_marshmallow(self)

    def process_fields(self) -> None:
        for _field in self.fields:
            if not _field.format._missing_lookup:
                continue

            if _field.format.lookup not in self._missing_lookups:
                self._missing_lookups[_field.format.lookup] = []
            self._missing_lookups[_field.format.lookup].append(_field.format)

    def add_field(self, new_field: SchemaField) -> None:
        if new_field.code in self._field_list:
            # Duplicates are skipped here because we're merging.
            return
        self._field_list.append(new_field.code)
        self.fields.append(new_field)

    def load_schemas(self) -> None:
        for _schema in self.schemata:
            if isinstance(_schema, Schema):
                for _field in _schema.fields:
                    self.add_field(_field)
                self._schema_list.append(_schema.code)
                continue

            if "fields" in _schema:
                _schemaname = f"schema_{len(self._schema_list)}"
                if "name" in _schema:
                    _schemaname = _schema["name"]
                self._schema_list.append(_schemaname)
                for dictfield in _schema["fields"]:
                    self.add_field(SchemaField(**dictfield))


@dataclass
class SchemaField:
    name: typing.AnyStr
    format: SchemaFieldFormat
    description: typing.AnyStr = field(default=None)
    code: typing.AnyStr = field(default=None)
    _value: typing.Any = field(init=False, default=None)

    def __post_init__(self):
        if not self.code:
            self.code = name_to_code(self.name)

        self.format = SchemaFieldFormat(**self.format)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        _rtn = {
            "name": self.__dict__["name"],
            "code": self.__dict__["code"],
            "format": self.format.export(),
        }
        if self.description:
            _rtn["description"] = self.__dict__["description"]
        return _rtn


@dataclass
class SchemaFieldFormat:
    type: typing.Optional[typing.AnyStr]
    values: typing.Optional[typing.Any] = None
    default_value: typing.Optional[typing.Any] = None
    lookup: typing.Optional[typing.Any] = None
    required: typing.Optional[bool] = field(default=False)
    readonly: typing.Optional[bool] = field(default=False)
    many: typing.Optional[bool] = field(default=False)
    markup: typing.Optional[typing.Dict] = field(default=None)
    validator: typing.Optional[typing.AnyStr] = field(default=None)
    connector_data: typing.Optional[typing.Dict[typing.AnyStr, typing.Any]] = field(
        default=None
    )
    _field: marshmallow_fields.Field = field(init=False, default=None)
    _missing_lookup: bool = field(init=False, default=False)

    def __post_init__(self):
        if self.type != "connector" and self.connector_data is not None:
            raise ValueError(
                "connector_data can only be supplied for fields of type `connector`"
            )

        self._generate_marshmallow_field()

    def attach_lookup(
        self, lookup_value: typing.Union[typing.List[typing.AnyStr], PyEnum]
    ):
        self.lookup = lookup_value
        self._generate_marshmallow_field()

    def export(self) -> typing.Dict[typing.AnyStr, typing.Any]:
        _fields = [
            "type",
            "values",
            "default_value",
            "lookup",
            "required",
            "readonly",
            "many",
            "markup",
            "validator",
            "connector_data",
        ]
        rtn = {}
        for _exportfield in _fields:
            if _exportfield == "lookup" and isinstance(
                self.__dict__[_exportfield], Enum
            ):
                rtn[_exportfield] = self.__dict__[_exportfield].code
                continue
            if self.__dict__[_exportfield]:
                rtn[_exportfield] = self.__dict__[_exportfield]
        return rtn

    def _get_mapped_fieldclass(self) -> typing.Callable:
        if self.type in SCHEMAFIELD_MAP:
            return SCHEMAFIELD_MAP[self.type]

        raise ValueError(f"Field format type `{self.type}` is invalid")

    def _get_field_params(self) -> typing.Union[None, typing.Dict]:  # noqa: C901
        _field_params = {}

        if self.required is not None:
            _field_params["required"] = self.required

        if self.readonly is True:
            _field_params["dump_only"] = True

        if self.type == "enum":
            self._missing_lookup = False
            if self.values:
                _field_params["enum"] = PyEnum("enum", self.values)
            elif self.lookup and isinstance(self.lookup, Enum):
                _field_params["enum"] = self.lookup.values
            else:
                self._missing_lookup = True
                return None

            if self.default_value:
                _field_params["dump_default"] = self._process_enum_default(
                    _field_params["enum"]
                )

        if self.type != "enum":
            if self.default_value is not None:
                _field_params["dump_default"] = self.default_value

        if self.validator and self.validator[:5] == "regex":
            _field_params["validate"] = RegexpValidator(
                regex=self.validator[6:], flags=re.IGNORECASE
            )

        if self.type not in SCHEMAFIELD_EXTATTR:
            return _field_params

        return {**_field_params, **SCHEMAFIELD_EXTATTR[self.type]}

    def _process_enum_default(self, enum_data: Enum):
        if not self.default_value:
            return None

        for _member in enum_data:
            if _member.name == self.default_value:
                return _member

        # TODO : Check for this much earlier
        raise ValueError("Invalid default value")

    def _generate_marshmallow_field(self):
        _field_params = self._get_field_params()
        if _field_params is None:
            return

        _field_class = self._get_mapped_fieldclass()
        if issubclass(_field_class, marshmallow_fields.Enum) and self.many:
            mapped_field = _field_class(enum=_field_params.get("enum"))
            del _field_params["enum"]
        else:
            mapped_field = _field_class(**_field_params)

        if not self.many:
            self._field = mapped_field
            return

        self._field = marshmallow_fields.List(
            mapped_field, **self._extract_default_params(_field_params)
        )

    def _extract_default_params(self, params: typing.Dict) -> typing.Dict:
        if not params:
            return None
        # .. dodge ..
        _std_fields = (
            "load_default",
            "missing",
            "dump_default",
            "default",
            "data_key",
            "attribute",
            "validate",
            "required",
            "allow_none",
            "load_only",
            "dump_only",
            "error_messages",
            "metadata",
        )
        return {k: params[k] for k in _std_fields if k in params}
