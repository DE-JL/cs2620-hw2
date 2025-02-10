import json
import struct

from config import PROTOCOL_TYPE
from entity import *


class DeleteUserRequest:
    """
    Delete user request.
    :var username: The username of the user to delete.
    """

    def __init__(self, username: str):
        self.username = username

    def __eq__(self, other):
        return self.username == other.username

    def __str__(self):
        return f"DeleteUserRequest({self.username})"

    def pack(self) -> bytes:
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")

            # Pack the data
            pack_format = f"!I {len(self.username)}s"
            data = struct.pack(pack_format, len(username_bytes), username_bytes)

            # Prepend the protocol header
            header = Header(RequestType.DELETE_USER.value, len(data))
            return header.pack() + data
        else:
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes) -> "DeleteUserRequest":
        if PROTOCOL_TYPE != "json":
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.DELETE_USER
            data = data[Header.SIZE:]

            # Unpack the data header
            header_format = "!I"
            username_len = struct.unpack_from(header_format, data)[0]
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{username_len}s"
            username_bytes = struct.unpack_from(data_format, data)[0]

            # Decode the data
            username = username_bytes.decode("utf-8")

            return DeleteUserRequest(username)
        else:
            # TODO
            raise Exception("json not implemented yet")


class DeleteUserResponse:
    """
    Delete user response.
    """

    def __init__(self):
        return

    def __eq__(self, other):
        return isinstance(other, DeleteUserResponse)

    def __str__(self):
        return "DeleteUserResponse()"

    @staticmethod
    def pack() -> bytes:
        if PROTOCOL_TYPE != "json":
            return Header(ResponseType.DELETE_USER.value).pack()
        else:
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes) -> "DeleteUserResponse":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.DELETE_USER

            return DeleteUserResponse()
        else:
            # TODO
            raise Exception("json not implemented yet")
