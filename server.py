import re
import selectors
import socket
import types
import uuid

from api import *
from config import HOST, PORT, DEBUG
from entity import *
from utils import parse_request, is_valid_regex


class Server:
    def __init__(self):
        # Initialize storage for users and messages
        self.users: dict[str, User] = {}
        self.messages: dict[uuid.UUID, Message] = {}

        # Create server socket
        self.sel = selectors.DefaultSelector()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setblocking(False)

    def run(self, host, port):
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
        Serve the connection.
        :param key: Connection key.
        :param mask: Mask for selecting events.
        """
        sock = key.fileobj
        ctx = key.data

        # Explicit type checking
        assert isinstance(sock, socket.socket)
        assert isinstance(ctx, types.SimpleNamespace)

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

            # Unpack the header and receive the payload
            header = Header.unpack(recvd)
            recvd += sock.recv(header.payload_size, socket.MSG_WAITALL)

            # Parse the request
            request = parse_request(RequestType(header.header_type), recvd)
            if DEBUG:
                print(f"Received request: {request}")

            # Handle the request
            self.handle_request(ctx, request)

        # Check if the socket is ready for writing
        if mask & selectors.EVENT_WRITE:
            # Only write to the socket if the outbound has data
            if ctx.outbound:
                sent = sock.send(ctx.outbound)
                ctx.outbound = ctx.outbound[sent:]

    def handle_request(self, ctx: types.SimpleNamespace, request: Request):
        match request:
            case EchoRequest():
                self.handle_echo(ctx, request)
            case AuthRequest():
                self.handle_auth(ctx, request)
            case GetMessagesRequest():
                self.handle_get_messages(ctx, request)
            case ListUsersRequest():
                self.handle_list_users(ctx, request)
            case SendMessageRequest():
                self.handle_send_message(ctx, request)
            case ReadMessagesRequest():
                self.handle_read_messages(ctx, request)
            case DeleteMessagesRequest():
                self.handle_delete_messages(ctx, request)
            case DeleteUserRequest():
                self.handle_delete_user(ctx, request)
            case _:
                print("Handle request: unknown request type.")
                exit(1)

    @classmethod
    def handle_echo(cls, ctx: types.SimpleNamespace, request: EchoRequest):
        resp = EchoResponse(request.string)
        ctx.outbound += resp.pack()

    def handle_auth(self, ctx: types.SimpleNamespace, request: AuthRequest):
        username, password = request.username, request.password
        match request.action_type:
            case AuthRequest.ActionType.CREATE_ACCOUNT:
                if self.users.get(username) is None:
                    self.users[username] = User(username=username, password=password)
                    resp = AuthResponse()
                else:
                    resp = ErrorResponse(f"Create account failed: user\"{username}\" already exists.")

            case AuthRequest.ActionType.LOGIN:
                if self.users.get(username) is None:
                    resp = ErrorResponse(f"Login failed: user \"{username}\" does not exist.")
                elif password != self.users[username].password:
                    resp = ErrorResponse(f"Login failed: incorrect password.")
                else:
                    self.users[username].login()
                    resp = AuthResponse()

            case _:
                print("Unknown AuthRequest action type")
                exit(1)

        # Send the response
        ctx.outbound += resp.pack()

    def handle_get_messages(self, ctx: types.SimpleNamespace, request: GetMessagesRequest):
        username = request.username
        assert username in self.users

        # Grab all messages associated with the user
        message_ids = self.users[username].message_ids
        messages = [self.messages[message_id] for message_id in message_ids]

        # Send the response
        resp = GetMessagesResponse(messages)
        ctx.outbound += resp.pack()

    def handle_list_users(self, ctx: types.SimpleNamespace, request: ListUsersRequest):
        pattern = request.pattern

        # Check if pattern is valid
        if not is_valid_regex(pattern):
            matches = []
        else:
            regex = re.compile(pattern)
            matches = [username for username in self.users if regex.search(username)]

        # Send the response
        resp = ListUsersResponse(matches)
        ctx.outbound += resp.pack()

    def handle_send_message(self, ctx: types.SimpleNamespace, request: SendMessageRequest):
        message = request.message
        assert message.id not in self.messages

        # Store the message
        self.messages[message.id] = message

        # Get the receiver
        assert message.receiver in self.users
        receiver = self.users[message.receiver]

        # Add the message ID
        receiver.add_message(message.id)

        # Send the response
        resp = SendMessageResponse()
        ctx.outbound += resp.pack()

    def handle_read_messages(self, ctx: types.SimpleNamespace, request: ReadMessagesRequest):
        username, message_ids = request.username, request.message_ids

        # Set the read flag for each message in the request
        for message_id in message_ids:
            # Grab the message
            assert message_id in self.messages
            message = self.messages[message_id]

            # Assert that the receiver matches the request username
            assert message.receiver == username

            # Mark the message as read
            message.set_read()

        # Send the response
        resp = ReadMessagesResponse()
        ctx.outbound += resp.pack()

    def handle_delete_messages(self, ctx: types.SimpleNamespace, request: DeleteMessagesRequest):
        username, message_ids = request.username, request.message_ids

        # Get the receiver
        assert username in self.users
        receiver = self.users[username]

        # Delete the messages one by one
        for message_id in message_ids:
            assert message_id in self.messages

            # Get the message to delete
            message = self.messages[message_id]

            # Assert that the receiver matches the request username
            assert message.receiver == username

            # Delete the message from the receiver
            receiver.delete_message(message_id)

            # Delete the message
            del self.messages[message_id]

        # Send the response
        resp = DeleteMessagesResponse()
        ctx.outbound += resp.pack()

    def handle_delete_user(self, ctx: types.SimpleNamespace, request: DeleteUserRequest):
        username = request.username

        # Get the user
        assert username in self.users
        user = self.users[username]

        # Delete all messages sent to that user
        for message_id in user.message_ids:
            assert message_id in self.messages
            del self.messages[message_id]

        # Delete the user
        del self.users[username]

        # Send the response
        resp = DeleteUserResponse()
        ctx.outbound += resp.pack()


def main():
    """
    Entry point for server application.
    :return: Nothing on success.
    """
    server = Server()
    server.run(HOST, PORT)


if __name__ == '__main__':
    main()
