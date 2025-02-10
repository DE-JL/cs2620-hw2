import json
import struct

from config import PROTOCOL_TYPE
from entity import *


class SendMessageRequest:
    """
    Send message request.
    :var message: Message object.
    """

    def __init__(self, username: str, message: Message):
        assert username == message.sender
        self.username = username
        self.message = message

    def __eq__(self, other):
        return (self.username == other.username and
                self.message == other.message)

    def __str__(self):
        return f"SendMessageRequest({self.message})"

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")

            # Pack the data
            pack_format = f"!I {len(self.username)}s"
            data = struct.pack(pack_format, len(username_bytes), username_bytes)
            data += self.message.pack()

            # Prepend the protocol header
            header = Header(RequestType.SEND_MESSAGE.value, len(data))
            return header.pack() + data
        else:
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.SEND_MESSAGE
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

            # Unpack the message
            message = Message.unpack(data)

            return SendMessageRequest(username, message)
        else:
            # TODO
            raise Exception("json not implemented yet")


class SendMessageResponse:
    """
    Send message response.
    """

    def __init__(self):
        return

    def __eq__(self, other):
        return isinstance(other, SendMessageResponse)

    def __str__(self):
        return "SendMessageResponse()"

    @staticmethod
    def pack() -> bytes:
        if PROTOCOL_TYPE != "json":
            return Header(ResponseType.SEND_MESSAGE.value).pack()
        else:
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes) -> "SendMessageResponse":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.SEND_MESSAGE

            return SendMessageResponse()
        else:
            # TODO
            raise Exception("json not implemented yet")
