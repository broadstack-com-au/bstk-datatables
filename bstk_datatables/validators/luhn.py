import re
import typing

from marshmallow import ValidationError
from marshmallow.validate import Validator


class LuhnValidator(Validator):
    """Validator which succeeds if the ``value`` matches passes a modulus 10 check.

    :param min_length: The minimum length of the number to check (including checkdigit)
    :param error: Error message to raise in case of a validation error.
        Can be interpolated with `{input}` and `{regex}`.
    """

    _min_length: int = None
    default_message = "Number does not appear to be valid."

    def __init__(
        self,
        min_length: typing.Optional[int] = 2,
        *,
        error: str | None = None,
    ):
        self._min_length = min_length
        self.error = error or self.default_message  # type: str

    def _repr_args(self) -> str:
        return f"min_length={self._min_length!r}"

    def _format_error(self) -> str:
        return self.error.format(min_length=self._min_length)

    @typing.overload
    def __call__(self, value: str) -> str:
        ...

    @typing.overload
    def __call__(self, value: bytes) -> bytes:
        ...

    def __call__(self, value):
        if not isinstance(value, str):
            value = str(value)

        value = re.sub("[^0-9]", "", value)
        if len(value) < self._min_length:
            raise ValidationError(self._format_error())

        digits = list(map(int, value))
        checksum = sum(
            (
                sum(digits[-1::-2]),
                sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]]),
            )
        )
        if checksum % 10 != 0:
            raise ValidationError(self._format_error())

        return value
