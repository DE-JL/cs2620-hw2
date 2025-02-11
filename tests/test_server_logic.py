import socket
import uuid
import pytest
import time
import subprocess

from api import *
from config import HOST, PORT
from entity import *


@pytest.fixture(scope="session", autouse=True)
def start_server():
    """Start the server before tests and ensure it shuts down after."""
    print("\nStarting server...")
    
    # Start the server process
    server_process = subprocess.Popen(["python", "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to be ready (adjust timeout if necessary)
    timeout = 5
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Try connecting to see if server is up
            sock = socket.create_connection((HOST, PORT), timeout=1)
            sock.close()
            print("Server is ready!")
            break
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    else:
        server_process.kill()
        pytest.exit("Server failed to start within timeout.")

    yield  # Tests run after this

    print("\nStopping server...")
    server_process.terminate()
    server_process.wait()  # Ensure process exits
    print("Server stopped.")


@pytest.fixture(scope="session")
def sock():
    """Fixture to create and close a socket connection before and after each test."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    yield client_socket  # This is what gets passed into test functions
    client_socket.close()  # Cleanup after each test


def recv_resp_bytes(sock: socket.socket) -> bytes:
    recvd = sock.recv(Header.SIZE, socket.MSG_WAITALL)
    assert recvd and len(recvd) == Header.SIZE

    header = Header.unpack(recvd)
    recvd += sock.recv(header.payload_size, socket.MSG_WAITALL)

    return recvd


def test_auth(sock: socket.socket):
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

    sock.sendall(req.pack())
    resp = ErrorResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.CREATE_ACCOUNT,
                      username="user1",
                      password="password")
    exp = AuthResponse()

    sock.sendall(req.pack())
    resp = AuthResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.CREATE_ACCOUNT,
                      username="user1",
                      password="password")
    exp = ErrorResponse(message="Create account failed: user \"user1\" already exists.")

    sock.sendall(req.pack())
    resp = ErrorResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user1",
                      password="wrong_password")
    exp = ErrorResponse(message="Login failed: incorrect password.")

    sock.sendall(req.pack())
    resp = ErrorResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    print("test_server_logic::test_auth ---- PASSED")


def test_send_and_get(sock: socket.socket):
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

    sock.sendall(req.pack())
    resp = AuthResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
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

    sock.sendall(req.pack())
    resp = ErrorResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
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

    sock.sendall(req.pack())
    resp = SendMessageResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
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

    sock.sendall(req.pack())
    resp = SendMessageResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user1")
    exp = GetMessagesResponse(messages=[])

    sock.sendall(req.pack())
    resp = GetMessagesResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")
    exp = GetMessagesResponse(messages=[msg1, msg2])

    sock.sendall(req.pack())
    resp = GetMessagesResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    print("test_server_logic::test_send_and_get ---- PASSED")


def test_list_users(sock: socket.socket):
    """
    This test case tests the following:
    1. List all users of the form user*.
    2. List all users of the form a*.
    """
    # ========================================== TEST ========================================== #
    req = ListUsersRequest(username="user1", pattern="user*")
    exp = ListUsersResponse(usernames=["user1", "user2"])

    sock.sendall(req.pack())
    resp = ListUsersResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = ListUsersRequest(username="user1", pattern="a*")
    exp = ListUsersResponse(usernames=[])

    sock.sendall(req.pack())
    resp = ListUsersResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    print("test_server_logic::test_list_users ---- PASSED")


def test_read_messages(sock: socket.socket):
    """
    This test case tests the following:
    1. Get the messages for user2 and assert that they are unread.
    1. Read messages for user2.
    2. Get the messages for user2 and assert that they are now read.
    """
    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")

    sock.sendall(req.pack())
    resp = GetMessagesResponse.unpack(recv_resp_bytes(sock))

    messages = resp.messages
    for message in messages:
        assert not message.read

    message_ids = [message.id for message in messages]
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = ReadMessagesRequest(username="user2",
                              message_ids=message_ids)
    exp = ReadMessagesResponse()

    sock.sendall(req.pack())
    resp = ReadMessagesResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")

    sock.sendall(req.pack())
    resp = GetMessagesResponse.unpack(recv_resp_bytes(sock))

    messages = resp.messages
    for message in messages:
        assert message.read
    # ========================================================================================== #

    print("test_server_logic::test_read_messages ---- PASSED")


def test_delete_messages(sock: socket.socket):
    """
    This test case tests the following:
    1. Get the messages for user2.
    2. Delete the messages for user2.
    3. Get the messages for user2 and assert that the inbox is empty.
    """
    # ========================================== TEST ========================================== #
    print("test_delete_messages --------------- starting")
    req = GetMessagesRequest(username="user2")

    sock.sendall(req.pack())
    resp = GetMessagesResponse.unpack(recv_resp_bytes(sock))

    messages = resp.messages
    message_ids = [message.id for message in messages]
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = DeleteMessagesRequest(username="user2",
                                message_ids=message_ids)
    exp = DeleteMessagesResponse()

    sock.sendall(req.pack())
    resp = DeleteMessagesResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = GetMessagesRequest(username="user2")
    exp = GetMessagesResponse(messages=[])

    sock.sendall(req.pack())
    resp = GetMessagesResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    print("test_server_logic::test_delete_messages ---- PASSED")


def test_delete_user(sock: socket.socket):
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

    sock.sendall(req.pack())
    resp = SendMessageResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = DeleteUserRequest(username="user2")
    exp = DeleteUserResponse()

    sock.sendall(req.pack())
    resp = DeleteUserResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user2",
                      password="password")
    exp = ErrorResponse(message="Login failed: user \"user2\" does not exist.")

    sock.sendall(req.pack())
    resp = ErrorResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    # ========================================== TEST ========================================== #
    req = AuthRequest(action_type=AuthRequest.ActionType.LOGIN,
                      username="user1",
                      password="password")
    exp = AuthResponse()

    sock.sendall(req.pack())
    resp = AuthResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
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

    sock.sendall(req.pack())
    resp = ErrorResponse.unpack(recv_resp_bytes(sock))

    assert resp == exp
    # ========================================================================================== #

    print("test_server_logic::test_delete_user ---- PASSED")


if __name__ == '__main__':
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Client connected to {HOST}:{PORT}")

    # Run tests (the order matters!)
    test_auth(client_socket)
    test_send_and_get(client_socket)
    test_list_users(client_socket)
    test_read_messages(client_socket)
    test_delete_messages(client_socket)
    test_delete_user(client_socket)
