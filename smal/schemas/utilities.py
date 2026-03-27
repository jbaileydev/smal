from pydantic import field_validator
import semver

class IdentifierValidationMixin:
    IDENTIFIER_FIELDS = ("name",)

    @field_validator(*IDENTIFIER_FIELDS)
    def validate_name_is_valid_identifier(cls, v: str) -> str:
        if not v.isidentifier():
            raise ValueError(f"Invalid identifier: {v}")
        return v


class SemverValidationMixin:
    SEMVER_FIELDS = ("version",)

    @field_validator(*SEMVER_FIELDS)
    def validate_semver(cls, v: str) -> str:
        try:
            semver.Version.parse(v)
        except (ValueError, TypeError):
            raise
        return v
