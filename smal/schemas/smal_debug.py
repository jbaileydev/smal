from pydantic import BaseModel, Field


class SMALDebugField(BaseModel):
    name: str = Field(..., description="The name of the debugging field.")
    type: str = Field(..., description="The type of the debugging field's data, e.g. uint8, uint16, enum:state, struct:Foo, etc.")
    offset_bytes: int = Field(..., description="The offset of this debugging field within its parent structure in bytes.")
    length_elements: int | None = Field(default=None, description="Length of the field in elements, if it is an array.")

class SMALNestedDebugStruct(BaseModel):
    name: str = Field(..., description="The name of the debugging structure.")
    size_bytes: int = Field(..., description="The size of the entire debugging structure in bytes.")
    fields: list[SMALDebugField] = Field(..., description="Fields of the debugging structure.")

class SMALDebugStruct(BaseModel):
    size_bytes: int = Field(..., description="The size of the entire debugging structure in bytes.")
    layout: list[SMALDebugField] = Field(..., description="The layout of the debugging structure, defined by fields.")
    nested_structs: list[SMALNestedDebugStruct] = Field(default_factory=list, description="Nested debugging structures that are utilized in this debugging structure, if any.")