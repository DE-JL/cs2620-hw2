from dataclasses import dataclass, field
import uuid


@dataclass
class User:
    username: str
    password: str
    message_ids: set[uuid.UUID] = field(default_factory=set)
    online: bool = field(default=True)

    def add_message(self, message_id: uuid.UUID):
        assert message_id not in self.message_ids
        self.message_ids.add(message_id)

    def delete_message(self, message_id: uuid.UUID):
        assert message_id in self.message_ids
        self.message_ids.remove(message_id)

    def login(self):
        self.online = True

    def logout(self):
        self.online = False
