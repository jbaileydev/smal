from pydantic import BaseModel, Field
from smal.schemas.utilities import IdentifierValidationMixin


class SMALError(IdentifierValidationMixin, BaseModel):
    IDENTIFIER_FIELDS = ("name",)

    name: str
    id: int
    description: str | None = Field(default=None, description="Description of the error, if any.")
