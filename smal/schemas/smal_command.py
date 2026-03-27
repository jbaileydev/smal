from pydantic import BaseModel, Field
from typing import Any, Literal
from smal.schemas.utilities import IdentifierValidationMixin

class SMALCommandParameter(IdentifierValidationMixin, BaseModel):
    IDENTIFIER_FIELDS = ("name",)

    name: str
    type: str
    default_value: Any = Field(default=None, description="The default value of the parameter, if any.")

class SMALCommandPayloadField(IdentifierValidationMixin, BaseModel):
    IDENTIFIER_FIELDS = ("name",)

    name: str
    type: str

class SMALCommandPayload(BaseModel):
    fields: list[SMALCommandPayloadField] = Field(default_factory=list, description="Fields of the command payload, if any.")

class SMALCommand(BaseModel):
    name: str
    direction: Literal["host_to_device", "device_to_host", "internal"]
    transport: Literal["ble", "protobuf", "uart", "spi", "i2c", "custom"]
    parameters: list[SMALCommandParameter] = Field(default_factory=list, description="Optional command parameters")
    payload: SMALCommandPayload | None = Field(default=None, description="Optional command payload.")
