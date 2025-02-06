import yaml

from protocol_custom import *


def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
        HOST = config["socket"]["host"]
        PORT = config["socket"]["default_port"]

    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Client connected to {HOST}:{PORT}")

    # Continuously send
    while True:
        s = input("> ")
        send_str(client_socket, s)


if __name__ == '__main__':
    main()
