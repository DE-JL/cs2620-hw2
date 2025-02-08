from enum import Enum
import struct
import yaml

with open("config.yaml") as _f:
    _config = yaml.safe_load(_f)
    PROTOCOL_TYPE = _config["protocol_type"]


class RequestType(Enum):
    DEBUG = 0
    AUTHENTICATE = 1
    GET_MESSAGES = 2
    SEND_MESSAGE = 3
    DELETE_MESSAGE = 4
    LIST_ACCOUNTS = 5


class ResponseType(Enum):
    DEBUG = 0
    AUTHENTICATE = 1
    GET_MESSAGES = 2
    SEND_MESSAGE = 3
    DELETE_MESSAGE = 4
    LIST_ACCOUNTS = 5
    ERROR = 6


class Header:
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
        return f"Header({self.header_type}, {self.payload_size})"

    def pack(self):
        return struct.pack(self.FORMAT, self.header_type, self.payload_size)

    @staticmethod
    def unpack(data: bytes):
        header_type, payload_size = struct.unpack_from(Header.FORMAT, data)
        return Header(header_type, payload_size)
