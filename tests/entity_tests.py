import json
import uuid

from entity import *


def test_message():
    msg0 = Message(sender="user0",
                   receiver="user1",
                   body="hello world")

    msg1 = Message.unpack(msg0.pack())
    assert msg0 == msg1


def test_user():
    id0 = uuid.UUID(int=0)
    id1 = uuid.UUID(int=1)

    message_ids0 = {id0, id1}
    message_ids1 = {id0, id1}

    user0 = User(username="user0",
                 password="password",
                 message_ids=message_ids0)
    user1 = User(username="user0",
                 password="password",
                 message_ids=message_ids1)

    assert user0 == user1


if __name__ == '__main__':
    test_message()
    test_user()
