import json
import uuid

from entity.header import *


class DeleteMessageRequest:
    """
    Delete message request.
    :var username: The username of the user trying to delete.
    :var message_id: uuid.UUID The UUID of the message to delete.
    """

    def __init__(self, username: str, message_id: uuid.UUID):
        self.username = username
        self.message_id = message_id

    def __str__(self):
        return f"DeleteMessageRequest({self.username}, {self.message_id})"

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")
            message_id_bytes = self.message_id.bytes

            # Pack the data
            pack_format = f"!I {len(username_bytes)}s 16s"
            data = struct.pack(pack_format,
                               len(username_bytes),
                               username_bytes, message_id_bytes)

            # Prepend the header
            header = Header(RequestType.DELETE_MESSAGE.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "username": self.username,
                "message_id": str(self.message_id)
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = Header(RequestType.DELETE_MESSAGE.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!I"
            username_len = struct.unpack_from(header_format, data)[0]
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{username_len}s 16s"
            username_bytes, message_id_bytes = struct.unpack_from(data_format, data)

            # Decode the data
            username = username_bytes.decode("utf-8")
            message_id = uuid.UUID(bytes=message_id_bytes)

            return DeleteMessageRequest(username, message_id)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)

            return DeleteMessageRequest(obj["username"],
                                        uuid.UUID(obj["message_id"]))
