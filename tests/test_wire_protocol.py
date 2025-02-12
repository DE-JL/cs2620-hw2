"""
This file primarily tests the correctness of the serialization methods defined by our wire protocol.

For each data, request, or response class, we test that an instance of that class can pack and unpack itself.
Since the two operations are expected to be inverses, we assert that the resulting object is equal to the original.

This function also tests that class objects whose fields are not value-equivalent are not compared as equal.
"""

import uuid

from api import *
from api.delete_messages import DeleteMessagesResponse
from api.delete_user import DeleteUserResponse
from entity import *


def test_header():
    header1 = Header(header_type=RequestType.ECHO.value,
                     payload_size=2620)
    header2 = Header(header_type=RequestType.ECHO.value,
                     payload_size=2621)

    assert header1 == Header.unpack(header1.pack())
    assert header2 == Header.unpack(header2.pack())
    assert header1 != header2


def test_message():
    msg1 = Message(sender="user1",
                   receiver="user2",
                   body="hello world",
                   id=uuid.UUID(int=0),
                   ts=0)
    msg2 = Message(sender="user1",
                   receiver="user2",
                   body="hello world!",
                   id=uuid.UUID(int=0),
                   ts=0)

    assert msg1 == Message.unpack(msg1.pack())
    assert msg2 == Message.unpack(msg2.pack())
    assert msg1 != msg2


def test_user():
    ids1 = {uuid.UUID(int=i) for i in range(3)}
    ids2 = {uuid.UUID(int=i) for i in range(4)}

    user1 = User(username="user1",
                 password="password",
                 message_ids=ids1.copy())
    user2 = User(username="user1",
                 password="password",
                 message_ids=ids2.copy())

    assert user1 != user2


def test_error():
    resp = ErrorResponse(message="error")
    assert resp == ErrorResponse.unpack(resp.pack())


def test_echo():
    # Request
    req1 = EchoRequest(string="hello world")
    req2 = EchoRequest(string="hello world!")

    assert req1 == EchoRequest.unpack(req1.pack())
    assert req2 == EchoRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    resp1 = EchoResponse(string="hello world")
    resp2 = EchoResponse(string="hello world!")

    assert resp1 == EchoResponse.unpack(resp1.pack())
    assert resp2 == EchoResponse.unpack(resp2.pack())
    assert resp1 != resp2


def test_auth():
    # Request
    req1 = AuthRequest(action_type=AuthRequest.ActionType.CREATE_ACCOUNT,
                       username="user1",
                       password="password")
    req2 = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                       username="user1",
                       password="password")

    assert req1 == AuthRequest.unpack(req1.pack())
    assert req2 == AuthRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    resp = AuthResponse()
    assert resp == AuthResponse.unpack(resp.pack())


def test_get_messages():
    # Request
    req1 = GetMessagesRequest(username="user1")
    req2 = GetMessagesRequest(username="user2")

    assert req1 == GetMessagesRequest.unpack(req1.pack())
    assert req2 == GetMessagesRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    message1 = Message(sender="user1",
                       receiver="user2",
                       body="hello world")
    message2 = Message(sender="user1",
                       receiver="user2",
                       body="hello world!")
    message3 = Message(sender="user1",
                       receiver="user2",
                       body="hello")
    resp1 = GetMessagesResponse(messages=[message1, message2])
    resp2 = GetMessagesResponse(messages=[message1, message3])

    assert resp1 == GetMessagesResponse.unpack(resp1.pack())
    assert resp2 == GetMessagesResponse.unpack(resp2.pack())
    assert resp1 != resp2


def test_list_users():
    # Request
    req1 = ListUsersRequest(username="user1", pattern="*")
    req2 = ListUsersRequest(username="user1", pattern="*+")

    assert req1 == ListUsersRequest.unpack(req1.pack())
    assert req2 == ListUsersRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    resp1 = ListUsersResponse(usernames=["user1", "user2"])
    resp2 = ListUsersResponse(usernames=["user1", "user3"])

    assert resp1 == ListUsersResponse.unpack(resp1.pack())
    assert resp2 == ListUsersResponse.unpack(resp2.pack())
    assert resp1 != resp2


def test_send_message():
    # Request
    req1 = SendMessageRequest(username="user1",
                              message=Message(sender="user1",
                                              receiver="user2",
                                              body="hello world",
                                              id=uuid.UUID(int=0),
                                              ts=0))

    req2 = SendMessageRequest(username="user1",
                              message=Message(sender="user1",
                                              receiver="user2",
                                              body="hello world",
                                              id=uuid.UUID(int=0),
                                              ts=1))

    assert req1 == SendMessageRequest.unpack(req1.pack())
    assert req2 == SendMessageRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    resp = SendMessageResponse()
    assert resp == SendMessageResponse.unpack(resp.pack())


def test_read_messages():
    # Request
    ids1 = [uuid.UUID(int=i) for i in range(3)]
    ids2 = [uuid.UUID(int=i) for i in range(4)]

    req1 = ReadMessagesRequest(username="user1", message_ids=ids1)
    req2 = ReadMessagesRequest(username="user1", message_ids=ids2)

    assert req1 == ReadMessagesRequest.unpack(req1.pack())
    assert req2 == ReadMessagesRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    resp = ReadMessagesResponse()
    assert resp == ReadMessagesResponse.unpack(resp.pack())


def test_delete_messages():
    # Request
    ids1 = [uuid.UUID(int=i) for i in range(3)]
    ids2 = [uuid.UUID(int=i) for i in range(4)]

    req1 = DeleteMessagesRequest(username="user1", message_ids=ids1)
    req2 = DeleteMessagesRequest(username="user1", message_ids=ids2)

    assert req1 == DeleteMessagesRequest.unpack(req1.pack())
    assert req2 == DeleteMessagesRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    resp = DeleteMessagesResponse()
    assert resp == DeleteMessagesResponse.unpack(resp.pack())


def test_delete_user():
    # Request
    req1 = DeleteUserRequest(username="user1")
    req2 = DeleteUserRequest(username="user2")

    assert req1 == DeleteUserRequest.unpack(req1.pack())
    assert req2 == DeleteUserRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    resp = DeleteUserResponse()
    assert resp == DeleteUserResponse.unpack(resp.pack())


if __name__ == '__main__':
    # Entity tests
    test_header()
    test_message()
    test_user()
    test_error()

    # Request response tests
    test_echo()
    test_auth()
    test_get_messages()
    test_list_users()
    test_send_message()
    test_read_messages()
    test_delete_messages()
    test_delete_user()
