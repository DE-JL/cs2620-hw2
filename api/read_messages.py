import json
import struct
import uuid

from .utils import pack_uuids, unpack_uuids
from config import PROTOCOL_TYPE
from entity import *


class ReadMessagesRequest:
    """
    Read messages request.
    :var message_ids: The IDs of the messages to be marked as read.
    """

    def __init__(self, username: str, message_ids: list[uuid.UUID]):
        self.username = username
        self.message_ids = message_ids

    def __eq__(self, other):
        return (self.username == other.username and
                self.message_ids == other.message_ids)

    def __str__(self):
        return f"ReadMessagesRequest({self.username}, {self.message_ids})"

    def pack(self):
        # Encode the data
        username_bytes = self.username.encode("utf-8")

        # Pack the data
        pack_format = f"!I {len(username_bytes)}s"
        data = struct.pack(pack_format, len(username_bytes), username_bytes)
        data += pack_uuids(self.message_ids)

        # Prepend the protocol header
        header = Header(ResponseType.READ_MESSAGES.value, len(data))
        return header.pack() + data

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.READ_MESSAGES
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

            return ReadMessagesRequest(username, message_ids)
        else:
            # TODO
            raise Exception("json not implemented yet")


class ReadMessagesResponse:
    """
    Read messages response.
    """

    def __init__(self):
        return

    def __eq__(self, other):
        return isinstance(other, ReadMessagesResponse)

    def __str__(self):
        return "ReadMessagesResponse()"

    @staticmethod
    def pack() -> bytes:
        if PROTOCOL_TYPE != "json":
            return Header(ResponseType.READ_MESSAGES.value).pack()
        else:
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes) -> "ReadMessagesResponse":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.READ_MESSAGES

            return ReadMessagesResponse()
        else:
            # TODO
            raise Exception("json not implemented yet")
