import selectors
import types
import yaml

from protocol_custom import *

# Selectors
sel = selectors.DefaultSelector()


def accept_wrapper(key: selectors.SelectorKey):
    """Accept a new client connection and register it for reading.
    :param key: Select key.
    """
    sock = key.fileobj

    # noinspection PyUnresolvedReferences
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")

    # We can store any per-connection state in 'data' if needed
    data = types.SimpleNamespace(addr=addr)
    sel.register(conn, selectors.EVENT_READ, data=data)


def service_connection(key, mask):
    """Echo incoming data back to the client; close on empty data."""
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        # Receive the header
        recvd = sock.recv(ProtocolHeader.SIZE, socket.MSG_WAITALL)

        # Check if the client closed the connection
        if not recvd or len(recvd) < ProtocolHeader.SIZE:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

        header = ProtocolHeader.unpack(recvd)
        print(f"Received header: {header}")

    # if mask & selectors.EVENT_WRITE:


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
