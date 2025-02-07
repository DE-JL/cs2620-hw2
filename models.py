from pydantic import BaseModel, Field
import time
import uuid

class Message(BaseModel):
    sender: str
    receiver: str
    body: str
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    ts: float = Field(default_factory=time.time)

class Account(BaseModel):
    name: str
    password: str
