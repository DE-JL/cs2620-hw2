import uuid
from fnmatch import fnmatch

from config import DEBUG
from entity import User
from generated.chat_pb2 import *
from generated.chat_pb2_grpc import *


class ChatServiceServicer(ChatServerServicer):
    """Main server class that manages users and message state for all clients."""

    def __init__(self):
        # Initialize storage for users and messages
        self.users: dict[str, User] = {}
        self.messages: dict[uuid.UUID, Message] = {}
        self.inbound_volume: int = 0
        self.outbound_volume: int = 0

    def Authenticate(self, request: AuthRequest, context: grpc.ServicerContext) -> AuthResponse:
        """
        This function handles all authentication requests: users creating an account or logging in.

        The function returns three possible errors to the client:
        1. Attempting to create an account with a username that already exists.
        2. Attempting to log into an account that doesn't exist.
        3. Attempting to log into an account with the wrong password.

        If there was an error, the server sends an ErrorResponse() object with a description to the client.
        On success, the server sends a blank AuthResponse() object to the client.

        :param request: The AuthRequest object.
        :param context: The servicer context.
        :rtype: AuthResponse
        """

        username, password = request.username, request.password
        match request.action_type:
            case AuthRequest.ActionType.CREATE_ACCOUNT:
                if username in self.users:
                    return AuthResponse(status=Status.ERROR,
                                        error_message=f"Create account failed: user \"{username}\" already exists.")
                else:
                    self.users[username] = User(username=username, password=password)
            case AuthRequest.ActionType.LOGIN:
                if username not in self.users:
                    resp = AuthResponse(status=Status.ERROR,
                                        error_message=f"Login failed: user \"{username}\" does not exist.")
                elif password != self.users[username].password:
                    resp = AuthResponse(status=Status.ERROR,
                                        error_message=f"Login failed: incorrect password.")
            case _:
                print("Unknown AuthRequest action type.")
                exit(1)

        return AuthResponse(status=Status.OK)

    def GetMessages(self, request: GetMessagesRequest, context: grpc.ServicerContext) -> GetMessagesResponse:
        """
        This function handles all get messages requests.

        It responds with a list of non-deleted messages that were sent to the requester.

        :param request: The GetMessagesRequest object.
        :param context: The servicer context.
        :rtype: GetMessagesResponse
        """
        username = request.username
        if username not in self.users:
            return GetMessagesResponse(messages=[])
        # TODO: fix on the client-side

        # Grab all messages associated with the user
        message_ids = self.users[username].message_ids
        messages = [self.messages[message_id] for message_id in message_ids]

        return GetMessagesResponse(status=Status.OK,
                                   messages=messages)

    def ListUsers(self, request: ListUsersRequest, context: grpc.ServicerContext) -> ListUsersResponse:
        """
        This function handles all list users requests.

        It responds with a list of all current users whose usernames match the provided wildcard pattern.

        :param request: The ListUsersRequest object.
        :param context: The servicer context.
        :rtype: GetMessagesResponse
        """
        username, pattern = request.username, request.pattern

        matches = [username for username in self.users if fnmatch(username, pattern)]
        if DEBUG:
            print(f"Pattern {pattern} matched users: {matches}")

        return ListUsersResponse(status=Status.OK,
                                 usernames=matches)

    def SendMessage(self, request: SendMessageRequest, context: grpc.ServicerContext) -> SendMessageResponse:
        """
        This function handles all send messages requests.

        It inserts the message into the map of message IDs to message objects.
        Then it inserts the message ID into the receiver's message inbox.
        On success, it responds with a blank SendMessageResponse() object.

        :param request: The SendMessageRequest object.
        :param context: The servicer context.
        :rtype: SendMessageResponse
        """
        username, message = request.username, request.message

        # Assert that the message does not already exist and the request user matches the sender
        assert message.id not in self.messages
        assert username == message.sender

        if message.recipient not in self.users:
            return SendMessageResponse(status=Status.ERROR,
                                       error_message=f"Send message failed: recipient \"{message.recipient}\" does not exist.")

        # Store the message
        message_id = uuid.UUID(bytes=message.id)
        self.messages[message_id] = message

        # Add the message to the receiver's inbox
        receiver = self.users[message.recipient]
        receiver.add_message(message_id)

        return SendMessageResponse(status=Status.OK)

    def ReadMessages(self, request: ReadMessagesRequest, context: grpc.ServicerContext) -> ReadMessagesResponse:
        """
        This function handles all read messages requests.

        It iterates over a list of message IDs.
        For each message ID, it gets the message object corresponding to the message ID.
        It sets the read flag of the message to true.
        On success, it responds with a blank ReadMessageResponse() object.

        :param request: The ReadMessagesRequest object.
        :param context: The servicer context.
        :rtype: ReadMessagesResponse
        """
        username, message_ids = request.username, request.message_ids

        # Set the read flag for each message in the request
        for message_id in message_ids:
            # Convert to UUID
            message_id = uuid.UUID(bytes=message_id)
            assert message_id in self.messages

            message = self.messages[message_id]

            # Assert that the receiver matches the request username
            assert message.recipient == username

            # Mark the message as read
            assert not message.read
            message.read = True

        return ReadMessagesResponse(status=Status.OK)

    def DeleteMessages(self, request: DeleteMessagesRequest, context: grpc.ServicerContext) -> DeleteMessagesResponse:
        """
        This function handles all delete messages requests.

        It iterates over a list of message IDs.
        For each message ID, it gets the message object corresponding to the message ID.
        It deletes the message object as well as the ID from the receiver's inbox.
        On success, it responds with a blank DeleteMessagesResponse() object.

        :param request: The DeleteMessagesRequest object.
        :param context: The servicer context.
        :rtype: DeleteMessagesResponse
        """
        username, message_ids = request.username, request.message_ids

        # Get the receiver
        receiver = self.users[username]

        # Delete the messages one by one
        for message_id in message_ids:
            # Convert to UUID
            message_id = uuid.UUID(bytes=message_id)
            assert message_id in self.messages

            # Get the message to delete
            message = self.messages[message_id]

            # Assert that the receiver matches the request username
            assert message.recipient == username

            # Delete the message from the receiver
            receiver.delete_message(message_id)

            # Delete the message
            del self.messages[message_id]

        return DeleteMessagesResponse(status=Status.OK)

    def DeleteUser(self, request: DeleteUserRequest, context: grpc.ServicerContext) -> DeleteUserResponse:
        """
        This function handles all delete user requests.

        It iterates over the list of message IDs in the deleted user's inbox.
        For each message ID, it erases the corresponding message object.
        The user is then removed from the server's state.
        On success, it responds with a blank DeleteUserResponse() object.

        :param request: The DeleteUserRequest object.
        :param context: The servicer context.
        :rtype: DeleteUserResponse
        """
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

        return DeleteUserResponse(status=Status.OK)

    def log(self):
        """Utility function that logs the state of the server."""
        print("\n-------------------------------- SERVER STATE --------------------------------")
        print(f"USERS: {self.users}")
        print(f"MESSAGES: {self.messages}")
        print(f"TOTAL TRAFFIC (INBOUND): {self.inbound_volume} bytes")
        print(f"TOTAL TRAFFIC (OUTBOUND): {self.outbound_volume} bytes")
        print("------------------------------------------------------------------------------\n")


def main():
    pass


if __name__ == '__main__':
    main()
