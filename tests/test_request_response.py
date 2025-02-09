import socket
import uuid

from api import *
from config import HOST, PORT
from entity import *


def test_auth(sock: socket.socket):
    auth_create = AuthRequest(AuthRequest.ActionType.CREATE_ACCOUNT,
                              "user0",
                              "password")
    sock.sendall(auth_create.pack())

    auth_login = AuthRequest(AuthRequest.ActionType.LOGIN,
                             "user0",
                             "password")
    sock.sendall(auth_login.pack())


def test_get_messages(sock: socket.socket):
    get_messages = GetMessagesRequest("user0")
    sock.sendall(get_messages.pack())

    recvd = sock.recv(Header.SIZE, socket.MSG_WAITALL)
    header = Header.unpack(recvd)

    assert ResponseType(header.header_type) == ResponseType.GET_MESSAGES
    recvd += sock.recv(header.payload_size, socket.MSG_WAITALL)
    resp = GetMessagesResponse.unpack(recvd)

    print(resp)


def test_list_users(sock: socket.socket):
    list_users = ListUsersRequest("user0", "*")
    sock.sendall(list_users.pack())


def test_send_message(sock: socket.socket):
    message = Message(sender="user0",
                      receiver="user1",
                      body="hello world",
                      id=uuid.UUID(int=0),
                      ts=0)
    send_message = SendMessageRequest(message)
    sock.sendall(send_message.pack())


def test_read_messages(sock: socket.socket):
    message_ids = [uuid.UUID(int=i) for i in range(4)]
    read_messages = ReadMessagesRequest("user0", message_ids)
    sock.sendall(read_messages.pack())


def test_delete_messages(sock: socket.socket):
    username = "user0"
    message_ids = [uuid.UUID(int=0), uuid.UUID(int=1)]

    delete_msg = DeleteMessagesRequest(username, message_ids)
    sock.sendall(delete_msg.pack())


def test_delete_user(sock: socket.socket):
    username = "user0"
    delete_user = DeleteUserRequest(username)
    sock.sendall(delete_user.pack())


if __name__ == '__main__':
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Client connected to {HOST}:{PORT}")

    # Request response connectivity testing
    test_auth(client_socket)
    test_get_messages(client_socket)
    test_list_users(client_socket)
    test_send_message(client_socket)
    test_read_messages(client_socket)
    test_delete_messages(client_socket)
    test_delete_user(client_socket)
