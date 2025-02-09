"""
This test file primarily tests the pack() and unpack() methods for our entity and request/response classes.
It also tests for equality checking.
"""

import uuid

from api import *
from entity import *


def test_header():
    header1 = Header(RequestType.ECHO.value, 2620)
    header2 = Header(RequestType.ECHO.value, 2621)

    assert header1 == Header.unpack(header1.pack())
    assert header2 == Header.unpack(header2.pack())
    assert header1 != header2

    print("pack_unpack::test_header ---- PASSED")


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

    print("pack_unpack::test_message ---- PASSED")


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

    print("pack_unpack::test_user ---- PASSED")


def test_auth():
    req1 = AuthRequest(AuthRequest.ActionType.CREATE_ACCOUNT,
                       "user1",
                       "password")
    req2 = AuthRequest(AuthRequest.ActionType.LOGIN,
                       "user1",
                       "password")

    assert req1 == AuthRequest.unpack(req1.pack())
    assert req2 == AuthRequest.unpack(req2.pack())
    assert req1 != req2

    print("pack_unpack::test_auth ---- PASSED")


def test_get_messages():
    # Request
    req1 = GetMessagesRequest("user1")
    req2 = GetMessagesRequest("user2")

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
    resp1 = GetMessagesResponse([message1, message2])
    resp2 = GetMessagesResponse([message1, message3])

    assert resp1 == GetMessagesResponse.unpack(resp1.pack())
    assert resp2 == GetMessagesResponse.unpack(resp2.pack())
    assert resp1 != resp2

    print("pack_unpack::test_get_messages ---- PASSED")


def test_list_users():
    # Request
    req1 = ListUsersRequest("user1", "*")
    req2 = ListUsersRequest("user1", "*+")

    assert req1 == ListUsersRequest.unpack(req1.pack())
    assert req2 == ListUsersRequest.unpack(req2.pack())
    assert req1 != req2

    # Response
    resp1 = ListUsersResponse(["user1", "user2"])
    resp2 = ListUsersResponse(["user1", "user3"])

    assert resp1 == ListUsersResponse.unpack(resp1.pack())
    assert resp2 == ListUsersResponse.unpack(resp2.pack())
    assert resp1 != resp2

    print("pack_unpack::test_list_users ---- PASSED")


def test_send_message():
    req1 = SendMessageRequest(Message(sender="user1",
                                      receiver="user2",
                                      body="hello world",
                                      id=uuid.UUID(int=0),
                                      ts=0))

    req2 = SendMessageRequest(Message(sender="user1",
                                      receiver="user2",
                                      body="hello world",
                                      id=uuid.UUID(int=0),
                                      ts=1))

    assert req1 == SendMessageRequest.unpack(req1.pack())
    assert req2 == SendMessageRequest.unpack(req2.pack())
    assert req1 != req2

    print("pack_unpack::test_send_message: ---- PASSED")


def test_read_messages():
    ids1 = [uuid.UUID(int=i) for i in range(3)]
    ids2 = [uuid.UUID(int=i) for i in range(4)]

    req1 = ReadMessagesRequest("user1", ids1)
    req2 = ReadMessagesRequest("user1", ids2)

    assert req1 == ReadMessagesRequest.unpack(req1.pack())
    assert req2 == ReadMessagesRequest.unpack(req2.pack())
    assert req1 != req2

    print("pack_unpack::test_read_messages ---- PASSED")


def test_delete_messages():
    ids1 = [uuid.UUID(int=i) for i in range(3)]
    ids2 = [uuid.UUID(int=i) for i in range(4)]

    req1 = DeleteMessagesRequest("user1", ids1)
    req2 = DeleteMessagesRequest("user1", ids2)

    assert req1 == DeleteMessagesRequest.unpack(req1.pack())
    assert req2 == DeleteMessagesRequest.unpack(req2.pack())
    assert req1 != req2

    print("pack_unpack::test_delete_messages: ---- PASSED")


def test_delete_user():
    req1 = DeleteUserRequest("user1")
    req2 = DeleteUserRequest("user2")

    assert req1 == DeleteUserRequest.unpack(req1.pack())
    assert req2 == DeleteUserRequest.unpack(req2.pack())
    assert req1 != req2

    print("pack_unpack::test_delete_user ---- PASSED")


if __name__ == '__main__':
    test_header()
    test_message()
    test_user()
    test_auth()
    test_get_messages()
    test_list_users()
    test_send_message()
    test_read_messages()
    test_delete_messages()
    test_delete_user()
