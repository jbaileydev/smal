from pydantic import field_validator
import semver
from typing import ClassVar

class IdentifierValidationMixin:
    IDENTIFIER_FIELDS: ClassVar[tuple[str]] = ("name",)

    @field_validator(*IDENTIFIER_FIELDS, check_fields=False)
    def validate_name_is_valid_identifier(cls, v: str) -> str:
        if not v.isidentifier():
            raise ValueError(f"Invalid identifier: {v}")
        return v


class SemverValidationMixin:
    SEMVER_FIELDS: ClassVar[tuple[str]] = ("version",)

    @field_validator(*SEMVER_FIELDS, check_fields=False)
    def validate_semver(cls, v: str) -> str:
        try:
            semver.Version.parse(v)
        except (ValueError, TypeError):
            raise
        return v
