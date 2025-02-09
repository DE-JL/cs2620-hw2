import json

from config import PROTOCOL_TYPE
from entity import *


class SendMessageRequest:
    """
    Send message request.
    :var message: Message object.
    """

    def __init__(self, message: Message):
        self.message = message

    def __eq__(self, other):
        return self.message == other.message

    def __str__(self):
        return f"SendMessageRequest({self.message})"

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Pack the message
            data = self.message.pack()

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

            # Unpack the message
            message = Message.unpack(data)

            return SendMessageRequest(message)
        else:
            # TODO
            raise Exception("json not implemented yet")
