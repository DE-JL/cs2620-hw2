import re
import selectors
import socket
import types
import uuid

from api import *
from config import HOST, PORT
from entity import *
from utils.parse import parse_request
from utils.regex import is_valid_regex


class Server:
    def __init__(self, host, port):
        # Initialize server variables
        self.users: dict[str, User] = {}
        self.messages: dict[uuid.UUID, Message] = {}

        # Create server socket
        self.sel = selectors.DefaultSelector()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(False)

        # Bind and listen on <host:port>
        self.server_socket.bind((host, port))
        self.server_socket.listen()

        print(f"Server listening on {host}:{port}")

        # Register the socket
        self.sel.register(self.server_socket, selectors.EVENT_READ, None)
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting.")
        finally:
            self.sel.close()

    def accept_wrapper(self, key: selectors.SelectorKey):
        """
        Accept a new client connection and register it for reading.
        :param key: Select key.
        """
        sock = key.fileobj
        if not isinstance(sock, socket.socket):
            raise TypeError("accept_wrapper expected a socket.socket")

        # Accept the connection
        conn, addr = sock.accept()
        print(f"Accepted client connection from: {addr}")

        # Set the connection to be non-blocking
        conn.setblocking(False)

        # Store a context namespace for this particular connection
        ctx = types.SimpleNamespace(addr=addr, outbound=b"")
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=ctx)

    def service_connection(self, key: selectors.SelectorKey, mask: int):
        """
        Echo incoming data back to the client; close on empty data.
        :param key: Connection key.
        :param mask: Mask for selecting events.
        """
        sock = key.fileobj
        ctx = key.data

        # Explicit type checking
        if not isinstance(sock, socket.socket):
            raise TypeError("service_connection::sock expected a socket.socket")
        if not isinstance(ctx, types.SimpleNamespace):
            raise TypeError("service_connection::ctx expected a types.SimpleNamespace")

        # Check if the socket is ready for reading
        if mask & selectors.EVENT_READ:
            # Receive the header
            recvd = sock.recv(Header.SIZE, socket.MSG_WAITALL)

            # Check if the client closed the connection
            if not recvd or len(recvd) != Header.SIZE:
                print(f"Closing connection to {ctx.addr}")
                self.sel.unregister(sock)
                sock.close()
                return

            # Unpack the header
            header = Header.unpack(recvd)
            print(f"Received header: {header}")

            # Receive the payload
            recvd += sock.recv(header.payload_size, socket.MSG_WAITALL)

            # Parse the request
            request = parse_request(RequestType(header.header_type), recvd)
            if request is None:
                string_bytes = recvd[Header.SIZE:]
                string = string_bytes.decode("utf-8")
                print(f"Received {RequestType(header.header_type)}: {string}")

                # Send it back
                ctx.outbound += recvd
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

        # Check if the socket is ready for writing
        if mask & selectors.EVENT_WRITE:
            # Only write to the socket if the outbound has data
            if ctx.outbound:
                sent = sock.send(ctx.outbound)
                ctx.outbound = ctx.outbound[sent:]

    def handle_request(self, sock: socket.socket, request: Request):
        pass

    def handle_auth(self, request: AuthRequest):
        username, password = request.username, request.password
        match request.action_type:
            case AuthRequest.ActionType.CREATE_ACCOUNT:
                if self.users.get(username) is None:
                    self.users[username] = User(username=username, password=password)
                else:
                    # TODO: return error code?
                    raise Exception(f"Create failed: user({username}) already exists")
            case AuthRequest.ActionType.LOGIN:
                if self.users.get(username) is None:
                    # TODO: return error code?
                    raise Exception(f"Login failed: user({username}) does not exist")
                else:
                    self.users[username].login()

    def handle_get_messages(self, request: GetMessagesRequest):
        username = request.username
        if username not in self.users:
            raise Exception(f"Get messages failed: username({username}) does not exist")

        # Grab all messages associated with the user
        message_ids = self.users[username].message_ids
        messages = [self.messages[message_id] for message_id in message_ids]

        # Sort them by order of timestamp
        sorted_messages = sorted(messages, key=lambda m: m.ts)

        resp = GetMessagesResponse(sorted_messages)
        return resp

    def handle_read_messages(self, request: ReadMessagesRequest):
        message_ids = request.message_ids

        # Set the read flag for each message in the request
        for message_id in message_ids:
            message = self.messages[message_id]
            message.set_read()

        resp = Header(ResponseType.OK.value, 0)
        return resp

    def handle_send_message(self, request: SendMessageRequest):
        message = request.message

        # Check that the message ID is unique
        if self.messages.get(message.id) is not None:
            raise Exception(f"Send message failed: message({message.id}) already exists")

        # Store the message
        self.messages[message.id] = message

        # Get the sender and the receiver
        sender_username, receiver_username = message.sender, message.receiver
        sender, receiver = self.users[sender_username], self.users[receiver_username]

        # Add the message ID to the sender and receiver
        sender.add_message(message.id)
        receiver.add_message(message.id)

        resp = Header(ResponseType.OK.value, 0)
        return resp

    def handle_delete_message(self, request: DeleteMessageRequest):
        message_id = request.message_id

        if self.messages.get(message_id) is None:
            raise Exception(f"Delete message failed: message({message_id}) does not exist")

        # Get the message to delete
        message = self.messages[message_id]

        # Get the sender and the receiver
        sender_username, receiver_username = message.sender, message.receiver
        sender, receiver = self.users[sender_username], self.users[receiver_username]

        # Delete the message ID from the sender and receiver
        sender.delete_message(message_id)
        receiver.delete_message(message_id)

        # Delete the message
        del self.messages[message_id]

        resp = Header(ResponseType.OK.value, 0)
        return resp

    def handle_list_users(self, request: ListUsersRequest):
        pattern = request.pattern

        # Check if pattern is valid
        if not is_valid_regex(pattern):
            matches = []
        else:
            regex = re.compile(pattern)
            matches = [username for username in self.users if regex.search(username)]

        resp = ListUsersResponse(matches)
        return resp


def main():
    """
    Entry point for server application.
    :return: Nothing on success.
    """
    server = Server(HOST, PORT)
    print(server.server_socket.getsockname())


if __name__ == '__main__':
    main()
