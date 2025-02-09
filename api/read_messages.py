import json
import uuid

from entity.header import *
from .utils import pack_uuids, unpack_uuids


class ReadMessagesRequest:
    """
    Read messages request.
    :var message_ids: The IDs of the messages to be marked as read.
    """

    def __init__(self, message_ids: list[uuid.UUID]):
        self.message_ids = message_ids

    def pack(self):
        # Pack the data
        data = pack_uuids(self.message_ids)

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

            # Unpack the data
            message_ids = unpack_uuids(data)

            return ReadMessagesRequest(message_ids)
        else:
            # TODO
            raise Exception("json not implemented yet")
