import socket

from api import *
from config import HOST, PORT
from entity import *


def main():
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Client connected to {HOST}:{PORT}")

    while True:
        s = input("> ")

        # Send the echo request
        req = EchoRequest(s)
        client_socket.send(req.pack())

        # Receive the header
        recvd = client_socket.recv(Header.SIZE, socket.MSG_WAITALL)
        assert recvd and len(recvd) == Header.SIZE

        # Unpack the header and receive the payload
        header = Header.unpack(recvd)
        recvd += client_socket.recv(header.payload_size, socket.MSG_WAITALL)

        # Unpack the response
        resp = EchoResponse.unpack(recvd)
        print(f"Echoed: {resp.string}")


if __name__ == '__main__':
    main()
