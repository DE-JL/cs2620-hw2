import socket
import uuid

from api import *
from config import HOST, PORT
from entity import *
from utils.parse import parse_request


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


def test_send_message(sock: socket.socket):
    message = Message(sender="user0",
                      receiver="user1",
                      body="hello world",
                      id=uuid.UUID(int=0),
                      ts=0)
    send_message = SendMessageRequest(message)

    sock.sendall(send_message.pack())


def test_delete_message(sock: socket.socket):
    username = "user0"
    message_id = uuid.UUID(int=0)

    delete_msg = DeleteMessageRequest(username, message_id)
    sock.sendall(delete_msg.pack())


def test_list_users(sock: socket.socket):
    list_users = ListUsersRequest("user0", "*")
    sock.sendall(list_users.pack())


def main():
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Client connected to {HOST}:{PORT}")

    # Wire protocol testing
    test_auth(client_socket)
    test_get_messages(client_socket)
    test_send_message(client_socket)
    test_delete_message(client_socket)
    test_list_users(client_socket)

    # Continuously send
    while True:
        s = input("> ")
        send_str(client_socket, s)

        # Receive the header
        recvd = client_socket.recv(Header.SIZE, socket.MSG_WAITALL)

        # Check if the client closed the connection
        if not recvd or len(recvd) != Header.SIZE:
            raise Exception("???????")

        # Unpack the header
        header = Header.unpack(recvd)
        print(f"Received header: {header}")

        # Receive the payload
        data = client_socket.recv(header.payload_size, socket.MSG_WAITALL)

        # Parse the request
        request = parse_request(RequestType(header.header_type), data)
        if request is None:
            s = data.decode("utf-8")
            print(f"Echo {RequestType(header.header_type)}: {s}")
        else:
            print(f"Echo {RequestType(header.header_type)}: {request}")


if __name__ == '__main__':
    main()
