from fnmatch import fnmatch
import selectors
import socket
import types
import uuid

from api import *
from config import DEBUG, LOCALHOST, PUBLIC_STATUS, SERVER_PORT
from entity import *
from utils import get_ipaddr, parse_request


class Server:
    """Main server class that manages users and message state for all clients."""

    def __init__(self):
        # Initialize storage for users and messages
        self.users: dict[str, User] = {}
        self.messages: dict[uuid.UUID, Message] = {}

        # Create server socket
        self.sel = selectors.DefaultSelector()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setblocking(False)

    def run(self, host: str, port: int):
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
        ctx = types.SimpleNamespace(addr=addr, outbound=b"", username=None)
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=ctx)

    def service_connection(self, key: selectors.SelectorKey, mask: int):
        """
        This function serves a connection.

        If the socket is receiving a request, it will:
        1. Read a fixed-size protocol header.
        2. Read a request whose size is given by the protocol header.
        3. Parse the request (whose type is given by the protocol header).
        4. Pass the request to the request handler.

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
                # Close the connection
                self.sel.unregister(sock)
                sock.close()
                print(f"Closed connection to {ctx.addr}")

                if DEBUG:
                    self.log()
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
            if DEBUG:
                self.log()

        # Send a response if it exists
        if mask & selectors.EVENT_WRITE:
            if ctx.outbound:
                sent = sock.send(ctx.outbound)
                ctx.outbound = ctx.outbound[sent:]

    def handle_request(self, ctx: types.SimpleNamespace, request: Request):
        """
        This function is called whenever a request is received.

        It forwards the request to the appropriate handler based on the request type.

        :param ctx: The connection context of the request.
        :param request: The request object.
        """
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
        resp = EchoResponse(string=request.string)
        ctx.outbound += resp.pack()

    def handle_auth(self, ctx: types.SimpleNamespace, request: AuthRequest):
        """
        This function handles all authentication requests: users creating an account or logging in.

        The function returns three possible errors back to the client:
        1. Attempting to create an account with a username that already exists.
        2. Attempting to log into an account that doesn't exist.
        3. Attempting to log into an account with the wrong password.

        If there was an error, the server sends an ErrorResponse() object with a description to the client.
        On success, the server sends a blank AuthResponse() object to the client.

        :param ctx: The connection context of the request.
        :param request: The authentication request object.
        :return: None
        """
        username, password = request.username, request.password
        match request.action_type:
            case AuthRequest.ActionType.CREATE_ACCOUNT:
                if username in self.users:
                    resp = ErrorResponse(message=f"Create account failed: user \"{username}\" already exists.")
                else:
                    self.users[username] = User(username=username, password=password)
                    resp = AuthResponse()

            case AuthRequest.ActionType.LOGIN:
                if username not in self.users:
                    resp = ErrorResponse(message=f"Login failed: user \"{username}\" does not exist.")
                elif password != self.users[username].password:
                    resp = ErrorResponse(message=f"Login failed: incorrect password.")
                else:
                    resp = AuthResponse()

            case _:
                print("Unknown AuthRequest action type.")
                exit(1)

        # Send the response
        ctx.outbound += resp.pack()

    def handle_get_messages(self, ctx: types.SimpleNamespace, request: GetMessagesRequest):
        """
        This function handles all get messages requests.

        It responds with a list of non-deleted messages that were sent to the requester.

        :param ctx: The connection context of the request.
        :param request: The get messages request object.
        """
        username = request.username

        # Grab all messages associated with the user
        message_ids = self.users[username].message_ids
        messages = [self.messages[message_id] for message_id in message_ids]

        # Send the response
        resp = GetMessagesResponse(messages=messages)
        ctx.outbound += resp.pack()

    def handle_list_users(self, ctx: types.SimpleNamespace, request: ListUsersRequest):
        """
        This function handles all list users requests.

        It responds with a list of all current users whose usernames match the provided wildcard pattern.

        :param ctx: The connection context of the request.
        :param request: The list users request object.
        """
        username, pattern = request.username, request.pattern

        matches = [username for username in self.users if fnmatch(username, pattern)]
        if DEBUG:
            print(f"Pattern {pattern} matched users: {matches}")

        # Send the response
        resp = ListUsersResponse(usernames=matches)
        ctx.outbound += resp.pack()

    def handle_send_message(self, ctx: types.SimpleNamespace, request: SendMessageRequest):
        """
        This function handles all send messages requests.

        It inserts the message into the map of message IDs to message objects.
        Then it inserts the message ID into the receiver's message inbox.
        On success, it responds with a blank SendMessageResponse() object.

        :param ctx:
        :param request:
        """
        username, message = request.username, request.message

        # Assert that the message does not already exist and the request user matches the sender
        assert message.id not in self.messages
        assert username == message.sender

        if message.receiver not in self.users:
            resp = ErrorResponse(message=f"Send message failed: recipient \"{message.receiver}\" does not exist.")
        else:
            # Store the message
            self.messages[message.id] = message

            # Add the message to the receiver's inbox
            receiver = self.users[message.receiver]
            receiver.add_message(message.id)

            resp = SendMessageResponse()

        # Send the response
        ctx.outbound += resp.pack()

    def handle_read_messages(self, ctx: types.SimpleNamespace, request: ReadMessagesRequest):
        """
        This function handles all read messages requests.

        It iterates over a list of message IDs.
        For each message ID, it gets the message object corresponding to the message ID.
        It sets the read flag of the message to true.
        On success, it responds with a blank ReadMessageResponse() object.

        :param ctx:
        :param request:
        """
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
        """
        This function handles all delete messages requests.

        It iterates over a list of message IDs.
        For each message ID, it gets the message object corresponding to the message ID.
        It deletes the message object as well as the ID from the receiver's inbox.
        On success, it responds with a blank DeleteMessagesResponse() object.

        :param ctx: The connection context of the request.
        :param request: The delete messages request object.
        """
        username, message_ids = request.username, request.message_ids

        # Get the receiver
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
        """
        This function handles all delete user requests.

        It iterates over the list of message IDs in the deleted user's inbox.
        For each message ID, it erases the corresponding message object.
        The user is then removed from the server's state.
        On success, it responds with a blank DeleteUserResponse() object.

        :param ctx: The connection context of the request.
        :param request: The delete user request object.
        """
        username = request.username

        # Get the user
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

    def log(self):
        """Utility function that logs the state of the server."""
        print("\n-------------------------------- SERVER STATE --------------------------------")
        print(f"USERS: {self.users}")
        print(f"MESSAGES: {self.messages}")
        print("------------------------------------------------------------------------------\n")


def main():
    """Entry point for server application."""

    if not PUBLIC_STATUS:
        host = LOCALHOST
    else:
        host = get_ipaddr()
        if host is None:
            print("Error: server IP address could not be found.")
            exit(1)

    server = Server()
    server.run(host, SERVER_PORT)


if __name__ == '__main__':
    main()
