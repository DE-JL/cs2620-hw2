from dataclasses import dataclass, field
import uuid

from .message import Message


@dataclass
class User:
    username: str
    password: str
    message_ids: set[uuid.UUID] = field(default_factory=set)
    online: bool = field(default=False)

    def add_message(self, message_id: uuid.UUID):
        if message_id in self.message_ids:
            raise Exception(f"Message {message_id} already exists")

        self.message_ids.add(message_id)

    def delete_message(self, message_id: uuid.UUID):
        if message_id not in self.message_ids:
            raise Exception(f"Message {message_id} does not exist")

        self.message_ids.remove(message_id)

    def login(self):
        self.online = True

    def logout(self):
        self.online = False
