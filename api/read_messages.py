import json
import uuid

from entity.header import *


class ReadMessagesRequest:
    """
    Read messages request.
    :var message_ids: The IDs of the messages to be marked as read.
    """

    def __init__(self, message_ids: list[uuid.UUID]):
        self.message_ids = message_ids

    def pack(self):
        # Pack the number of message IDs
        data = struct.pack("!I", len(self.message_ids))
        data = data[struct.calcsize("!I"):]

        # Pack the message IDs one by one
        for message_id in self.message_ids:
            data += struct.pack("!16s", message_id.bytes)

        # Prepend the header
        header = Header(ResponseType.LIST_USERS.value, len(data))
        return header.pack() + data

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            message_ids = []

            # First unpack the number of message IDs
            num_message_ids = struct.unpack_from("!I", data)[0]
            data = data[struct.calcsize("!I"):]

            # Unpack the message IDs one by one
            for _ in range(num_message_ids):
                message_id_bytes = struct.unpack_from("!16s", data)[0]
                message_id = uuid.UUID(bytes=message_id_bytes)
                message_ids.append(message_id)
                data = data[struct.calcsize("!16s"):]

            return ReadMessagesRequest(message_ids)
        else:
            # TODO
            raise Exception("json not implemented yet")
