"""
This file tests the core logic functions of the server class.

A server is instantiated at the start of this file -- it will not bind to any socket.

In each test case, a server request handler is manually called with a request object.
For each call to a request handler, the server will write the response to a context object.
Since we are "mocking" a client connection, we can pass a blank context with the outbound attribute set.

Each request has a hardcoded expectation -- the response that is correct.
After each request, we read the bytes that the server wrote to the context.
We assert that the response bytes match the packed representation of the expected object.
"""

import types
import uuid

import server

from api import *
from entity import *

# Initialize server and context
svr = server.Server()
ctx = types.SimpleNamespace(outbound=b"")


def read_resp() -> bytes:
    """
    Utility function to simulate consuming the response bytes from the server.
    :return: The outbound bytes set by the server.
    """
    assert ctx.outbound is not None
    resp = ctx.outbound
    ctx.outbound = b""

    return resp


def test_auth():
    """
    This test case tests the following:
    1. Log in to an account that doesn't exist.
    2. Create an account that already exists.
    3. Logging in with an incorrect password.
    4. Successful account creation and login.
    """
    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user1",
                      password="password")
    exp = ErrorResponse(message="Login failed: user \"user1\" does not exist.")

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.CREATE_ACCOUNT,
                      username="user1",
                      password="password")
    exp = AuthResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.CREATE_ACCOUNT,
                      username="user1",
                      password="password")
    exp = ErrorResponse(message="Create account failed: user \"user1\" already exists.")

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user1",
                      password="wrong_password")
    exp = ErrorResponse(message="Login failed: incorrect password.")

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #


def test_send_and_get():
    """
    This test case tests the following:
    1. Send a message to a user that doesn't exist.
    2. Send a message from user1 to user2.
    3. Retrieve the messages from user1 and user2.
    """
    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.CREATE_ACCOUNT,
                      username="user2",
                      password="password")
    exp = AuthResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    invalid_msg = Message(sender="user1",
                          receiver="user3",
                          body="hello user3!",
                          id=uuid.UUID(int=0),
                          ts=0)
    req = SendMessageRequest(username="user1",
                             message=invalid_msg)
    exp = ErrorResponse(message="Send message failed: recipient \"user3\" does not exist.")

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    msg1 = Message(sender="user1",
                   receiver="user2",
                   body="hello user2!",
                   id=uuid.UUID(int=1),
                   ts=1)
    req = SendMessageRequest(username="user1",
                             message=msg1)
    exp = SendMessageResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    msg2 = Message(sender="user1",
                   receiver="user2",
                   body="how are you doing, user2?",
                   id=uuid.UUID(int=2),
                   ts=2)
    req = SendMessageRequest(username="user1",
                             message=msg2)
    exp = SendMessageResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user1")
    exp = GetMessagesResponse(messages=[])

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")
    exp = GetMessagesResponse(messages=[msg1, msg2])

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #


def test_list_users():
    """
    This test case tests the following:
    1. List all users of the form user*.
    2. List all users of the form a*.
    """
    # ========================================== TEST ========================================== #
    req = ListUsersRequest(username="user1", pattern="user*")
    exp = ListUsersResponse(usernames=["user1", "user2"])

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = ListUsersRequest(username="user1", pattern="a*")
    exp = ListUsersResponse(usernames=[])

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #


def test_read_messages():
    """
    This test case tests the following:
    1. Get the messages for user2 and assert that they are unread.
    1. Read messages for user2.
    2. Get the messages for user2 and assert that they are now read.
    """
    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")

    svr.handle_request(ctx, req)
    resp = read_resp()
    resp = GetMessagesResponse.unpack(resp)

    messages = resp.messages
    for message in messages:
        assert not message.read

    message_ids = [message.id for message in messages]
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = ReadMessagesRequest(username="user2",
                              message_ids=message_ids)
    exp = ReadMessagesResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")

    svr.handle_request(ctx, req)
    resp = read_resp()
    resp = GetMessagesResponse.unpack(resp)

    messages = resp.messages
    for message in messages:
        assert message.read
    # ========================================================================================== #


def test_delete_messages():
    """
    This test case tests the following:
    1. Get the messages for user2.
    2. Delete the messages for user2.
    3. Get the messages for user2 and assert that the inbox is empty.
    """
    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")

    svr.handle_request(ctx, req)
    resp = read_resp()
    resp = GetMessagesResponse.unpack(resp)

    messages = resp.messages
    message_ids = [message.id for message in messages]
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = DeleteMessagesRequest(username="user2",
                                message_ids=message_ids)
    exp = DeleteMessagesResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")
    exp = GetMessagesResponse(messages=[])

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #


def test_delete_user():
    """
    This test case tests the following:
    1. Send a message to user2 so that it has a non-empty inbox.
    2. Delete user2.
    3. Assert that attempting to log in to user2 now fails.
    4. Log in to user1.
    5. Assert that a message to user2 now fails: user not found.
    """
    # ========================================== TEST ========================================== #
    msg = Message(sender="user1",
                  receiver="user2",
                  body="hello user2!",
                  id=uuid.UUID(int=1),
                  ts=1)
    req = SendMessageRequest(username="user1",
                             message=msg)
    exp = SendMessageResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = DeleteUserRequest(username="user2")
    exp = DeleteUserResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user2",
                      password="password")
    exp = ErrorResponse(message="Login failed: user \"user2\" does not exist.")

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user1",
                      password="password")
    exp = AuthResponse()

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    msg = Message(sender="user1",
                  receiver="user2",
                  body="are you still alive",
                  id=uuid.UUID(int=0),
                  ts=0)
    req = SendMessageRequest(username="user1",
                             message=msg)
    exp = ErrorResponse(message="Send message failed: recipient \"user2\" does not exist.")

    svr.handle_request(ctx, req)
    resp = read_resp()
    assert resp == exp.pack()
    # ========================================================================================== #


if __name__ == '__main__':
    # Run tests (the order matters!)
    test_auth()
    test_send_and_get()
    test_list_users()
    test_read_messages()
    test_delete_messages()
    test_delete_user()
