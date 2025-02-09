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

        # Pack the message IDs one by one
        for message_id in self.message_ids:
            data += struct.pack("!16s", message_id.bytes)

        # Prepend the protocol header
        header = Header(ResponseType.LIST_USERS.value, len(data))
        return header.pack() + data

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Discard the protocol header
            data = data[Header.SIZE:]

            # Unpack the data header
            header_format = "!I"
            num_message_ids = struct.unpack_from(header_format, data)[0]
            data = data[struct.calcsize(header_format):]

            # Unpack the message IDs one by one
            message_ids = []
            for _ in range(num_message_ids):
                # Unpack the message
                message_id_bytes = struct.unpack_from("!16s", data)[0]
                message_id = uuid.UUID(bytes=message_id_bytes)
                data = data[struct.calcsize("!16s"):]

                # Append to the list
                message_ids.append(message_id)

            return ReadMessagesRequest(message_ids)
        else:
            # TODO
            raise Exception("json not implemented yet")
