import json
import struct
import uuid

from .utils import pack_uuids, unpack_uuids
from config import PROTOCOL_TYPE
from entity import *


class DeleteMessagesRequest:
    """
    Delete message request.
    :var username: The username of the user trying to delete.
    :var message_ids: The list of IDs of the messages to delete.
    """

    def __init__(self, username: str, message_ids: list[uuid.UUID]):
        self.username = username
        self.message_ids = message_ids

    def __eq__(self, other):
        return (self.username == other.username and
                self.message_ids == other.message_ids)

    def __str__(self):
        return f"DeleteMessageRequest({self.username}, {self.message_ids})"

    def pack(self) -> bytes:
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")

            # Pack the data
            pack_format = f"!I {len(username_bytes)}s"
            data = struct.pack(pack_format, len(username_bytes), username_bytes)
            data += pack_uuids(self.message_ids)

            # Prepend the protocol header
            header = Header(RequestType.DELETE_MESSAGES.value, len(data))
            return header.pack() + data
        else:
            # TODO: discard protocol header
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes) -> "DeleteMessagesRequest":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.DELETE_MESSAGES
            data = data[Header.SIZE:]

            # Unpack the data header
            header_format = "!I"
            username_len = struct.unpack_from(header_format, data)[0]
            data = data[struct.calcsize(header_format):]

            # Unpack and decode the username
            data_format = f"!{username_len}s"
            username_bytes = struct.unpack_from(data_format, data)[0]
            username = username_bytes.decode("utf-8")
            data = data[struct.calcsize(data_format):]

            # Unpack the message IDs
            message_ids = unpack_uuids(data)

            return DeleteMessagesRequest(username, message_ids)
        else:
            # TODO: discard protocol header
            raise Exception("json not implemented yet")


class DeleteMessagesResponse:
    """
    Delete messages response.
    """

    def __init__(self):
        return

    def __eq__(self, other):
        return isinstance(other, DeleteMessagesResponse)

    def __str__(self):
        return "DeleteMessagesResponse()"

    @staticmethod
    def pack() -> bytes:
        if PROTOCOL_TYPE != "json":
            return Header(ResponseType.DELETE_MESSAGES.value).pack()
        else:
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes) -> "DeleteMessagesResponse":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.DELETE_MESSAGES

            return DeleteMessagesResponse()
        else:
            # TODO
            raise Exception("json not implemented yet")
