import socket

from api import *
from config import HOST, PORT
from entity import *
from utils.parse import parse_request


def main():
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Client connected to {HOST}:{PORT}")

    # Continuously send
    while True:
        s = input("> ")
        send_str(client_socket, s)

        # Receive the header
        recvd = client_socket.recv(Header.SIZE, socket.MSG_WAITALL)
        assert recvd and len(recvd) == Header.SIZE

        # Unpack the header
        header = Header.unpack(recvd)
        print(f"Received header: {header}")

        # Receive the payload
        recvd += client_socket.recv(header.payload_size, socket.MSG_WAITALL)

        # Parse the request
        request = parse_request(RequestType(header.header_type), recvd)
        assert request is None

        s = recvd[Header.SIZE:].decode("utf-8")
        print(f"Echoed: {s}")


if __name__ == '__main__':
    main()
