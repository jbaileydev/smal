from pydantic import BaseModel
from smal.schemas.utilities import IdentifierValidationMixin


class SMALEvent(IdentifierValidationMixin, BaseModel):
    IDENTIFIER_FIELDS = ("name",)

    name: str
    id: int