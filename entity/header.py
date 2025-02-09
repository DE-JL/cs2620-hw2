from enum import Enum
import struct

from config import PROTOCOL_TYPE


class RequestType(Enum):
    DEBUG = 0
    AUTHENTICATE = 1
    GET_MESSAGES = 2
    READ_MESSAGES = 3
    SEND_MESSAGE = 4
    DELETE_MESSAGE = 5
    LIST_USERS = 6


class ResponseType(Enum):
    OK = 0
    AUTHENTICATE = 1
    GET_MESSAGES = 2
    READ_MESSAGES = 3
    SEND_MESSAGE = 4
    DELETE_MESSAGE = 5
    LIST_USERS = 6
    ERROR = 7


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

    def pack(self) -> bytes:
        if PROTOCOL_TYPE != "json":
            return struct.pack(self.FORMAT, self.header_type, self.payload_size)
        else:
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes) -> "Header":
        if PROTOCOL_TYPE != "json":
            header_type, payload_size = struct.unpack_from(Header.FORMAT, data)
            return Header(header_type, payload_size)
        else:
            # TODO
            raise Exception("json not implemented yet")
