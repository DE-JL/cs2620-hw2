from protocol import *


def test_authenticate(sock: socket.socket):
    auth_create = Authenticate(Authenticate.ActionType.CREATE_ACCOUNT,
                               "user0",
                               "password")
    sock.sendall(auth_create.pack())

    auth_login = Authenticate(Authenticate.ActionType.LOGIN,
                              "user0",
                              "password")
    sock.sendall(auth_login.pack())


def test_send_message(sock: socket.socket):
    body = "hello world"
    message_id = uuid.UUID(int=0)
    timestamp = 0

    send_msg = SendMessage("user0",
                           "user1",
                           body,
                           message_id,
                           timestamp)
    sock.sendall(send_msg.pack())


def test_delete_message(sock: socket.socket):
    username = "user0"
    message_id = uuid.UUID(int=0)

    delete_msg = DeleteMessage(username, message_id)
    sock.sendall(delete_msg.pack())


def test_list_accounts(sock: socket.socket):
    list_accs = ListAccounts("user0", "*")
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
    test_authenticate(client_socket)
    test_send_message(client_socket)
    test_delete_message(client_socket)
    test_list_accounts(client_socket)

    # Continuously send
    while True:
        s = input("> ")
        send_str(client_socket, s)


if __name__ == '__main__':
    main()
