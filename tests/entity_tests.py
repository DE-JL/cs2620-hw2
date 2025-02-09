import json

from entity import *


def test_message():
    msg = Message(sender="user0",
                  receiver="user1",
                  body="hello world")

    # msg.message_id = uuid.UUID(int=0)
    print(msg.read)
    msg.set_read()
    print(msg.read)

    obj_str = json.dumps({**msg.__dict__, "id": str(msg.id)})
    obj = json.loads(obj_str)
    print(obj)


if __name__ == '__main__':
    test_message()
