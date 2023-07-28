import pytest
from marshmallow import ValidationError

from bstk_datatables.validators.luhn import LuhnValidator


def test_luhn_validator_standard_pass():
    validator = LuhnValidator()
    validator("4987654321098769")


def test_luhn_validator_standard_fail():
    validator = LuhnValidator()
    with pytest.raises(ValidationError):
        validator("4987654321098768")


def test_luhn_validator_messy_pass():
    validator = LuhnValidator()
    validator("4-987-6543-2109-876-9")
