from pydantic import BaseModel, Field
from smal.schemas.smal_state import SMALState
from smal.schemas.smal_event import SMALEvent
from smal.schemas.smal_command import SMALCommand
from smal.schemas.smal_error import SMALError
from smal.schemas.smal_message import SMALMessage
from smal.schemas.smal_transition import SMALTransition
from smal.schemas.smal_debug import SMALDebugStruct
from smal.schemas.utilities import IdentifierValidationMixin, SemverValidationMixin

class SMALFile(IdentifierValidationMixin, SemverValidationMixin, BaseModel):
    IDENTIFIER_FIELDS = ("machine",)
    SEMVER_FIELDS = ("version",)

    machine: str = Field(..., description="Name of this state machine.")
    version: str = Field(..., description="Semantic version (major.minor.patch) of this state machine.")
    states: list[SMALState] = Field(..., description="States associated with this state machine.")
    events: list[SMALEvent] = Field(default_factory=list, description="Events associated with this state machine, if any.")
    commands: list[SMALCommand] = Field(default_factory=list, description="Commands associated with this state machine, if any.")
    errors: list[SMALError] = Field(default_factory=list, description="Errors associated with this state machine, if any.")
    messages: list[SMALMessage] = Field(default_factory=list, description="Messages associated with this state machine, if any.")
    transitions: list[SMALTransition] = Field(default_factory=list, description="State transitions associated with this state machine, if any.")
    debug: SMALDebugStruct | None = Field(default=None, description="Debugging structure associated with this state machine, if any.")
    description: str | None = Field(default=None, description="Description of the state machine.")
