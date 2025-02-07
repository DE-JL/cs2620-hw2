from enum import Enum
import json
import socket
import struct
import uuid
import yaml

with open("config.yaml") as _f:
    _config = yaml.safe_load(_f)
    _PROTOCOL_TYPE = _config["protocol_type"]


class RequestType(Enum):
    DEBUG = 0
    AUTHENTICATE = 1
    SEND_MESSAGE = 2
    READ_MESSAGES = 3
    DELETE_MESSAGE = 4
    LIST_ACCOUNTS = 5
    ERR = 6


class ResponseCode(Enum):
    DEBUG = 0
    OK = 1


class ProtocolHeader:
    """
    Header for wire protocol.
    :var FORMAT: Predefined protocol header format.
    :var SIZE: Predefined protocol header size.
    """

    FORMAT = "!B I"
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, header_type: int, payload_size=0):
        self.header_type = header_type
        self.payload_size = payload_size

    def __str__(self):
        return f"ProtocolHeader({self.header_type}, {self.payload_size})"

    def pack(self):
        return struct.pack(self.FORMAT, self.header_type, self.payload_size)

    @staticmethod
    def unpack(data: bytes):
        header_type, payload_size = struct.unpack(ProtocolHeader.FORMAT, data)
        return ProtocolHeader(header_type, payload_size)


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
        LOGIN = 1

    def __init__(self, action_type: ActionType, username: str, password: str):
        self.action_type = action_type
        self.username = username
        self.password = password

    def __str__(self):
        return f"Authenticate({self.action_type}, {self.username}, {self.password})"

    def pack(self):
        if _PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")
            password_bytes = self.password.encode("utf-8")

            # Pack the data
            pack_format = f"!B I I {len(username_bytes)}s {len(password_bytes)}s"
            data = struct.pack(pack_format,
                               self.action_type.value,
                               len(username_bytes), len(password_bytes),
                               username_bytes, password_bytes)

            # Prepend the header
            header = ProtocolHeader(RequestType.AUTHENTICATE.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "action_type": self.action_type.value,
                "username": self.username,
                "password": self.password
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = ProtocolHeader(RequestType.AUTHENTICATE.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if _PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!B I I"
            header_size = struct.calcsize(header_format)
            action_type_value, username_len, password_len = struct.unpack(header_format, data[:header_size])

            # Unpack the data
            data_format = f"!{username_len}s {password_len}s"
            username_bytes, password_bytes = struct.unpack(data_format, data[header_size:])

            # Decode the data
            username = username_bytes.decode("utf-8")
            password = password_bytes.decode("utf-8")

            return Authenticate(Authenticate.ActionType(action_type_value),
                                username,
                                password)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)

            return Authenticate(Authenticate.ActionType(obj["action_type"]),
                                obj["username"],
                                obj["password"])


class SendMessage:
    """
    Send message operator.
    :var sender: The username of the sender.
    :var receiver: The username of the recipient.
    :var message_id: The id of the message.
    :var body: The body (text) of the message.
    :var timestamp: The timestamp of the message.
    """

    def __init__(self, sender: str, receiver: str, body: str, message_id: uuid.UUID, timestamp: float):
        self.sender = sender
        self.receiver = receiver
        self.body = body
        self.message_id = message_id
        self.timestamp = timestamp

    def __str__(self):
        return (f"SendMessage({self.sender}, {self.receiver}, {self.body},"
                f" {self.message_id}, {self.timestamp})")

    def pack(self):
        if _PROTOCOL_TYPE != "json":
            # Encode the data
            sender_bytes = self.sender.encode("utf-8")
            receiver_bytes = self.receiver.encode("utf-8")
            body_bytes = self.body.encode("utf-8")
            message_id_bytes = self.message_id.bytes

            # Pack the data
            pack_format = f"!I I I {len(sender_bytes)}s {len(receiver_bytes)}s {len(body_bytes)}s 16s d"
            data = struct.pack(pack_format,
                               len(sender_bytes), len(receiver_bytes), len(body_bytes),
                               sender_bytes, receiver_bytes, body_bytes,
                               message_id_bytes, self.timestamp)

            # Prepend the header
            header = ProtocolHeader(RequestType.SEND_MESSAGE.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "sender": self.sender,
                "receiver": self.receiver,
                "body": self.body,
                "message_id": str(self.message_id),
                "timestamp": self.timestamp
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = ProtocolHeader(RequestType.SEND_MESSAGE.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if _PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!I I I"
            header_size = struct.calcsize(header_format)
            sender_len, receiver_len, body_len = struct.unpack(header_format, data[:header_size])

            # Unpack the data
            data_format = f"!{sender_len}s {receiver_len}s {body_len}s 16s d"
            sender_bytes, receiver_bytes, body_bytes, message_id_bytes, timestamp = struct.unpack(data_format, data[header_size:])

            # Decode the data
            sender = sender_bytes.decode("utf-8")
            receiver = receiver_bytes.decode("utf-8")
            body = body_bytes.decode("utf-8")
            message_id = uuid.UUID(bytes=message_id_bytes)

            return SendMessage(sender, receiver, body, message_id, timestamp)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)
            print(obj)

            return SendMessage(obj["sender"],
                               obj["receiver"],
                               obj["body"],
                               uuid.UUID(obj["message_id"]),
                               obj["timestamp"])


class DeleteMessage:
    """
    Delete message operator.
    :var username: The username of the user trying to delete.
    :var message_id: uuid.UUID The UUID of the message to delete.
    """

    def __init__(self, username: str, message_id: uuid.UUID):
        self.username = username
        self.message_id = message_id

    def __str__(self):
        return f"DeleteMessage({self.username}, {self.message_id})"

    def pack(self):
        if _PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")
            message_id_bytes = self.message_id.bytes

            # Pack the data
            pack_format = f"!I {len(username_bytes)}s 16s"
            data = struct.pack(pack_format,
                               len(username_bytes),
                               username_bytes, message_id_bytes)

            # Prepend the header
            header = ProtocolHeader(RequestType.DELETE_MESSAGE.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "username": self.username,
                "message_id": str(self.message_id)
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = ProtocolHeader(RequestType.DELETE_MESSAGE.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if _PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!I"
            header_size = struct.calcsize(header_format)
            username_len = struct.unpack(header_format, data[:header_size])[0]

            # Unpack the data
            data_format = f"!{username_len}s 16s"
            username_bytes, message_id_bytes = struct.unpack(data_format, data[header_size:])

            # Decode the data
            username = username_bytes.decode("utf-8")
            message_id = uuid.UUID(bytes=message_id_bytes)

            return DeleteMessage(username, message_id)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)

            return DeleteMessage(obj["username"],
                                 uuid.UUID(obj["message_id"]))


class ListAccounts:
    """
    List accounts operator.
    :var username: The username of the user requesting accounts matching pattern.
    :var pattern: The regex pattern to match.
    """

    def __init__(self, username: str, pattern: str):
        self.username = username
        self.pattern = pattern

    def __str__(self):
        return f"ListAccounts({self.username}, {self.pattern})"

    def pack(self):
        if _PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")
            pattern_bytes = self.pattern.encode("utf-8")

            # Pack the data
            pack_format = f"!I I {len(username_bytes)}s {len(pattern_bytes)}s"
            data = struct.pack(pack_format,
                               len(username_bytes), len(pattern_bytes),
                               username_bytes, pattern_bytes)

            # Prepend the header
            header = ProtocolHeader(RequestType.LIST_ACCOUNTS.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "username": self.username,
                "pattern": self.pattern
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = ProtocolHeader(RequestType.LIST_ACCOUNTS.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if _PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!I I"
            header_size = struct.calcsize(header_format)
            username_len, pattern_len = struct.unpack(header_format, data[:header_size])

            # Unpack the data
            data_format = f"!{username_len}s {pattern_len}s"
            username_bytes, pattern_bytes = struct.unpack(data_format, data[header_size:])

            # Decode the data
            username = username_bytes.decode("utf-8")
            pattern = pattern_bytes.decode("utf-8")

            return ListAccounts(username, pattern)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)

            return ListAccounts(obj["username"],
                                obj["pattern"])


def parse_request(header: ProtocolHeader, data: bytes):
    request_type = RequestType(header.header_type)
    match request_type:
        case RequestType.DEBUG:
            return None
        case RequestType.AUTHENTICATE:
            return Authenticate.unpack(data)
        case RequestType.SEND_MESSAGE:
            return SendMessage.unpack(data)
        case RequestType.READ_MESSAGES:
            raise Exception("Not implemented yet")
        case RequestType.DELETE_MESSAGE:
            return DeleteMessage.unpack(data)
        case RequestType.LIST_ACCOUNTS:
            return ListAccounts.unpack(data)


def send_str(sock: socket.socket, s: str):
    """
    A utility function that wires a string (for logging).
    :param sock: Target socket.
    :param s: The string to send.
    """
    s_bytes = s.encode("utf-8")
    header = ProtocolHeader(RequestType.DEBUG.value, len(s_bytes))
    sock.sendall(header.pack() + s_bytes)
