from pydantic import BaseModel

class SMALTransition(BaseModel):
    trigger_state: str
    trigger_evt: str
    action: str
    nxt_state: str
    nxt_state_entry_evt: str
