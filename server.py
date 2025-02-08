import selectors
import socket
import types
import yaml

from entity import *
from api import *

# Selectors
sel = selectors.DefaultSelector()


def accept_wrapper(key: selectors.SelectorKey):
    """
    Accept a new client connection and register it for reading.
    :param key: Select key.
    """
    sock = key.fileobj
    # noinspection PyUnresolvedReferences
    conn, addr = sock.accept()
    print(f"Accepted client connection from: {addr}")

    # Set the connection to be non-blocking
    conn.setblocking(False)

    # Store a context namespace for this particular connection
    ctx = types.SimpleNamespace(addr=addr, outbound=b"")
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=ctx)


def service_connection(key, mask):
    """
    Echo incoming data back to the client; close on empty data.
    :param key: Connection key.
    :param mask: Mask for selecting events.
    """
    sock = key.fileobj
    ctx = key.data

    if mask & selectors.EVENT_READ:
        # Receive the header
        recvd = sock.recv(Header.SIZE, socket.MSG_WAITALL)

        # Check if the client closed the connection
        if not recvd or len(recvd) != Header.SIZE:
            print(f"Closing connection to {ctx.addr}")
            sel.unregister(sock)
            sock.close()
            return

        # Unpack the header
        header = Header.unpack(recvd)
        print(f"Received header: {header}")

        # Receive the payload
        data = sock.recv(header.payload_size, socket.MSG_WAITALL)

        # Parse the request
        request = parse_request(header, data)
        if request is None:
            s = data.decode("utf-8")
            print(f"Received {RequestType(header.header_type)}: {s}")

            # Send it back
            ctx.outbound += header.pack() + data
        elif type(request) == GetMessagesRequest:
            print(f"Received {RequestType(header.header_type)}: {request}")

            message0 = Message(sender="user0",
                               receiver="user1",
                               body="hello world")
            message1 = Message(sender="user0",
                               receiver="user2",
                               body="hello world")

            resp = GetMessagesResponse([message0, message1])
            ctx.outbound += resp.pack()
        else:
            print(f"Received {RequestType(header.header_type)}: {request}")

    if mask & selectors.EVENT_WRITE:
        if ctx.outbound is not None:
            sent = sock.send(ctx.outbound)
            ctx.outbound = ctx.outbound[sent:]


def main():
    """
    Entry point for server application.
    :return: Nothing on success.
    """
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
        HOST = config["socket"]["host"]
        PORT = config["socket"]["default_port"]

    # Create a server socket, bind and listen on IP:port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.setblocking(False)
    print(f"Server listening on {HOST}:{PORT}")

    # Register
    sel.register(server_socket, selectors.EVENT_READ, None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting.")
    finally:
        sel.close()


if __name__ == '__main__':
    main()
