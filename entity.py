from dataclasses import dataclass
import uuid


@dataclass
class Account:
    name: str
    password: str


@dataclass
class Message:
    text: str
    sender: str
    receiver: str
    timestamp: float  # epoch time
    id: uuid.UUID
