from enum import Enum
import socket
import struct
import uuid


class HeaderType(Enum):
    NOOP = 0
    REQUEST = 1
    RESPONSE = 2
    LOG = 3


class RequestType(Enum):
    AUTHENTICATE = 1
    SEND_MESSAGE = 2
    DELETE_MESSAGE = 3
    READ_MESSAGES = 4
    LIST_ACCOUNTS = 5
    ERR = 6


class ResponseCode(Enum):
    OK = 0


class ProtocolHeader:
    """
    Header for wire protocol.
    :var FORMAT: Predefined protocol header format.
    :var SIZE: Predefined protocol header size.
    """

    FORMAT = "!B I"
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, header_type=HeaderType.NOOP, size=0):
        self.header_type = header_type
        self.size = size

    def __str__(self):
        return f"ProtocolHeader: ({self.header_type}, {self.size})"

    def pack(self):
        return struct.pack(self.FORMAT, self.header_type.value, self.size)

    @staticmethod
    def unpack(bytestream: bytes):
        header_type_value, size = struct.unpack(ProtocolHeader.FORMAT, bytestream)
        return ProtocolHeader(HeaderType(header_type_value), size)


class Authenticate:
    """
    Authenticate operator.
    :type Authenticate.ActionType: An enum for the types of possible authentication actions.
    :var action_type: The realized action type.
    :var username: The username of the user attempting to authenticate.
    :var password: The password of the user attempting to authenticate.
    """

    class ActionType(Enum):
        CREATE_ACCOUNT = 0
        DELETE_ACCOUNT = 1

    def __init__(self, action_type: ActionType, username: str, password: str):
        self.action_type = action_type
        self.username = username
        self.password = password

    def pack(self):
        # Encode the username and password
        username_bytes = self.username.encode("utf-8")
        password_bytes = self.password.encode("utf-8")

        # Pack the bytes together
        pack_format = f"B I I {len(username_bytes)}s {len(password_bytes)}"
        return struct.pack(pack_format,
                           self.action_type.value,
                           len(username_bytes), len(password_bytes),
                           username_bytes, password_bytes)

    @staticmethod
    def unpack(bytestream: bytes):
        # Unpack the header
        header_format = "!B I I"
        header_size = struct.calcsize(header_format)
        action_type_value, username_len, password_len = struct.unpack(header_format, bytestream[:header_size])

        # Unpack username and password
        data_format = f"!{username_len}s {password_len}s"
        username_bytes, password_bytes = struct.unpack(data_format, bytestream[header_size:])

        # Decode username and password
        username = username_bytes.decode("utf-8")
        password = password_bytes.decode("utf-8")

        return Authenticate(Authenticate.ActionType(action_type_value), username, password)


class SendMessage:
    """
    Send message operator.
    :var sender: The username of the sender.
    :var receiver: The username of the recipient.
    :var body: The body (text) of the message.
    """

    def __init__(self, sender: str, receiver: str, body: str):
        self.sender = sender
        self.receiver = receiver
        self.body = body

    def pack(self):
        # Encode the sender, receiver, and body
        sender_bytes = self.sender.encode("utf-8")
        receiver_bytes = self.receiver.encode("utf-8")
        body_bytes = self.body.encode("utf-8")

        # Pack the bytes together
        pack_format = f"I I I {len(sender_bytes)}s {len(receiver_bytes)}s {len(body_bytes)}s"
        return struct.pack(pack_format,
                           len(sender_bytes), len(receiver_bytes), len(body_bytes),
                           sender_bytes, receiver_bytes, body_bytes)

    @staticmethod
    def unpack(bytestream: bytes):
        # Unpack the header
        header_format = "!I I I"
        header_size = struct.calcsize(header_format)
        sender_len, receiver_len, body_len = struct.unpack(header_format, bytestream[:header_size])

        # Unpack sender, receiver, and body
        data_format = f"!{sender_len}s {receiver_len}s {body_len}s"
        sender_bytes, receiver_bytes, body_bytes = struct.unpack(data_format, bytestream[header_size:])

        # Decode sender, receiver, and body
        sender = sender_bytes.decode("utf-8")
        receiver = receiver_bytes.decode("utf-8")
        body = body_bytes.decode("utf-8")

        return SendMessage(sender, receiver, body)


class DeleteMessage:
    """
    Delete message operator.
    :var username: The username of the user trying to delete.
    :var message_id: uuid.UUID The UUID of the message to delete.
    """

    def __init__(self, username: str, message_id: uuid.UUID):
        self.username = username
        self.message_id = message_id

    def pack(self):
        # Encode the string and message_id
        username_bytes = self.username.encode("utf-8")
        message_id_bytes = self.message_id.bytes

        # Pack the bytes together
        pack_format = f"I {len(username_bytes)}s 16s"
        return struct.pack(pack_format,
                           len(username_bytes),
                           username_bytes, message_id_bytes)

    @staticmethod
    def unpack(bytestream: bytes):
        # Unpack the header
        header_format = "!I"
        header_size = struct.calcsize(header_format)
        username_len = struct.unpack(header_format, bytestream[:header_size])[0]

        # Unpack username and message_id
        data_format = f"!{username_len}s 16s"
        username_bytes, message_id_bytes = struct.unpack(data_format, bytestream[header_size:])

        # Decode username and message_id
        username = username_bytes.decode("utf-8")
        message_id = uuid.UUID(bytes=message_id_bytes)

        return DeleteMessage(username, message_id)


def parse_payload(header_type: HeaderType, payload: bytes):
    match HeaderType:
        case HeaderType.NOOP:
            pass
        case HeaderType.REQUEST:
            pass
        case HeaderType.RESPONSE:
            pass
        case HeaderType.LOG:
            pass


def wire(sock: socket.socket, header_type: HeaderType, bytestream: bytes):
    """
    A utility function that implements the wire protocol.
    :param sock: Target socket.
    :param header_type: The header type.
    :param bytestream: The raw bytes of the payload.
    """

    header = ProtocolHeader(header_type, len(bytestream))
    sock.sendall(header.pack())
    sock.sendall(bytestream)


def send_str(sock: socket.socket, s: str):
    """
    A utility function that wires a string (for logging).
    :param sock: Target socket.
    :param s: The string to send.
    """

    s_bytes = s.encode("utf-8")
    wire(sock, HeaderType.LOG, s_bytes)
