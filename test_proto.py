"""
This file tests the integration of the server and the client with PyTest fixtures.

A server process is initialized and kept alive for the duration of all test cases.
For each test case, a client process is started and connection is established between the server and the client.

Each test case consists of a client submitting a variety of requests.
Every request will have a hardcoded expectation response object.
The test case asserts that all responses match their expectations.
"""

import grpc
import uuid
import pytest
import time
import subprocess

from chat_pb2 import *
from chat_pb2_grpc import *
from config import LOCALHOST, SERVER_PORT

# @pytest.fixture(scope="session", autouse=True)
# def start_server():
#     """Start the server before tests and ensure it shuts down after."""
#     print("\nStarting server...")
#
#     # Start the server process
#     server_process = subprocess.Popen(["python", "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
#     # Wait for server to be ready (adjust timeout if necessary)
#     timeout = 5
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         try:
#             # Try connecting to see if server is up
#             sock = socket.create_connection((LOCALHOST, SERVER_PORT), timeout=1)
#             sock.close()
#             print("Server is ready!")
#             break
#         except (ConnectionRefusedError, OSError):
#             time.sleep(1)
#     else:
#         server_process.kill()
#         pytest.exit("Server failed to start within timeout.")
#
#     # Tests run after this
#     yield
#
#     print("\nStopping server...")
#     server_process.terminate()
#     server_process.wait()
#     print("Server stopped.")
#
#
# @pytest.fixture(scope="session")
# def sock():
#     """Fixture to create and close a socket connection before and after each test."""
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_socket.connect((LOCALHOST, SERVER_PORT))
#     yield client_socket  # This is what gets passed into test functions
#     client_socket.close()  # Cleanup after each test

channel = grpc.insecure_channel(f"{LOCALHOST}:{SERVER_PORT}")
stub = ChatServerStub(channel)
print("client connected to the server")


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
    exp = AuthResponse(status=Status.ERROR,
                       error_message="Login failed: user \"user1\" does not exist.")

    resp = stub.Authenticate(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.CREATE_ACCOUNT,
                      username="user1",
                      password="password")
    exp = AuthResponse(status=Status.SUCCESS)

    resp = stub.Authenticate(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.CREATE_ACCOUNT,
                      username="user1",
                      password="password")
    exp = AuthResponse(status=Status.ERROR,
                       error_message="Create account failed: user \"user1\" already exists.")

    resp = stub.Authenticate(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user1",
                      password="wrong_password")
    exp = AuthResponse(status=Status.ERROR,
                       error_message="Login failed: incorrect password.")

    resp = stub.Authenticate(req)
    assert resp == exp
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
    exp = AuthResponse(status=Status.SUCCESS)

    resp = stub.Authenticate(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    invalid_msg = Message(id=uuid.UUID(int=0).bytes,
                          sender="user1",
                          recipient="user3",
                          body="hello user3!",
                          timestamp=0)
    req = SendMessageRequest(username="user1",
                             message=invalid_msg)
    exp = SendMessageResponse(status=Status.ERROR,
                              error_message="Send message failed: recipient \"user3\" does not exist.")

    resp = stub.SendMessage(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    msg1 = Message(id=uuid.UUID(int=1).bytes,
                   sender="user1",
                   recipient="user2",
                   body="hello user2!",
                   timestamp=1)
    req = SendMessageRequest(username="user1",
                             message=msg1)
    exp = SendMessageResponse(status=Status.SUCCESS)

    resp = stub.SendMessage(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    msg2 = Message(id=uuid.UUID(int=2).bytes,
                   sender="user1",
                   recipient="user2",
                   body="how are you doing, user2?",
                   timestamp=2)
    req = SendMessageRequest(username="user1",
                             message=msg2)
    exp = SendMessageResponse(status=Status.SUCCESS)

    resp = stub.SendMessage(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user1")
    exp = GetMessagesResponse(status=Status.SUCCESS,
                              messages=[])

    resp = stub.GetMessages(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")
    exp = GetMessagesResponse(status=Status.SUCCESS,
                              messages=[msg1, msg2])

    resp = stub.GetMessages(req)
    assert resp == exp
    # ========================================================================================== #


def test_list_users():
    """
    This test case tests the following:
    1. List all users of the form user*.
    2. List all users of the form a*.
    """
    # ========================================== TEST ========================================== #
    req = ListUsersRequest(username="user1", pattern="user*")
    exp = ListUsersResponse(status=Status.SUCCESS,
                            usernames=["user1", "user2"])

    resp = stub.ListUsers(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = ListUsersRequest(username="user1", pattern="a*")
    exp = ListUsersResponse(usernames=[])

    resp = stub.ListUsers(req)
    assert resp == exp
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
    resp = stub.GetMessages(req)

    messages = resp.messages
    for message in messages:
        assert not message.read

    message_ids = [message.id for message in messages]
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = ReadMessagesRequest(username="user2",
                              message_ids=message_ids)
    exp = ReadMessagesResponse(status=Status.SUCCESS)

    resp = stub.ReadMessages(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")
    resp = stub.GetMessages(req)

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
    resp = stub.GetMessages(req)

    messages = resp.messages
    message_ids = [message.id for message in messages]
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = DeleteMessagesRequest(username="user2",
                                message_ids=message_ids)
    exp = DeleteMessagesResponse(status=Status.SUCCESS)

    resp = stub.DeleteMessages(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")
    exp = GetMessagesResponse(status=Status.SUCCESS,
                              messages=[])

    resp = stub.GetMessages(req)
    assert resp == exp
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
    msg = Message(id=uuid.UUID(int=1).bytes,
                  sender="user1",
                  recipient="user2",
                  body="hello user2!")
    req = SendMessageRequest(username="user1",
                             message=msg)
    exp = SendMessageResponse(status=Status.SUCCESS)

    resp = stub.SendMessage(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = DeleteUserRequest(username="user2")
    exp = DeleteUserResponse(status=Status.SUCCESS)

    resp = stub.DeleteUser(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user2",
                      password="password")
    exp = AuthResponse(status=Status.ERROR,
                       error_message="Login failed: user \"user2\" does not exist.")

    resp = stub.Authenticate(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user1",
                      password="password")
    exp = AuthResponse(status=Status.SUCCESS)

    resp = stub.Authenticate(req)
    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    msg = Message(id=uuid.UUID(int=0).bytes,
                  sender="user1",
                  recipient="user2",
                  body="are you still alive")
    req = SendMessageRequest(username="user1",
                             message=msg)
    exp = SendMessageResponse(status=Status.ERROR,
                              error_message="Send message failed: recipient \"user2\" does not exist.")

    resp = stub.SendMessage(req)
    assert resp == exp
    # ========================================================================================== #


if __name__ == '__main__':
    # Connect to the server
    test_auth()
    test_send_and_get()
    test_list_users()
    test_read_messages()
    test_delete_messages()
    test_delete_user()

    channel.close()
