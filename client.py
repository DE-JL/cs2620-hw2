import socket
import uuid
import yaml

from entity import *
from api import *


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
    recvd = sock.recv(header.payload_size, socket.MSG_WAITALL)
    resp = GetMessagesResponse.unpack(recvd)

    print(resp)


def test_send_message(sock: socket.socket):
    body = "hello world"
    message_id = uuid.UUID(int=0)
    timestamp = 0

    send_msg = SendMessageRequest("user0",
                                  "user1",
                                  body,
                                  message_id,
                                  timestamp)
    sock.sendall(send_msg.pack())


def test_delete_message(sock: socket.socket):
    username = "user0"
    message_id = uuid.UUID(int=0)

    delete_msg = DeleteMessageRequest(username, message_id)
    sock.sendall(delete_msg.pack())


def test_list_accounts(sock: socket.socket):
    list_accs = ListAccountsRequest("user0", "*")
    sock.sendall(list_accs.pack())


def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
        HOST = config["socket"]["host"]
        PORT = config["socket"]["default_port"]

    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Client connected to {HOST}:{PORT}")

    # Wire protocol testing
    test_auth(client_socket)
    test_get_messages(client_socket)
    test_send_message(client_socket)
    test_delete_message(client_socket)
    test_list_accounts(client_socket)

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
        request = parse_request(header, data)
        if request is None:
            s = data.decode("utf-8")
            print(f"Echo {RequestType(header.header_type)}: {s}")
        else:
            print(f"Echo {RequestType(header.header_type)}: {request}")


if __name__ == '__main__':
    main()
