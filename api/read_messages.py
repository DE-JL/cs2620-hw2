import struct
import uuid

from pydantic import BaseModel

from .utils import pack_uuids, unpack_uuids
from config import PROTOCOL_TYPE
from entity import *


class ReadMessagesRequest(BaseModel):
    username: str
    message_ids: list[uuid.UUID]

    def pack(self):
        """
        Serialization format:
            <HEADER> <USERNAME_LEN> <USERNAME_BYTES> <LIST[MESSAGE_ID]>
        """
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")

            # Pack the data
            pack_format = f"!I {len(username_bytes)}s"
            data = struct.pack(pack_format, len(username_bytes), username_bytes)
            data += pack_uuids(self.message_ids)

            # Prepend the protocol header
            header = Header(header_type=ResponseType.READ_MESSAGES.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=ResponseType.READ_MESSAGES.value,
                            payload_size=len(data))
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

            return ReadMessagesRequest(username=username,
                                       message_ids=message_ids)
        else:
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.READ_MESSAGES
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return ReadMessagesRequest.model_validate_json(json_str)


class ReadMessagesResponse(BaseModel):
    @staticmethod
    def pack() -> bytes:
        return Header(header_type=ResponseType.READ_MESSAGES.value).pack()

    @staticmethod
    def unpack(data: bytes) -> "ReadMessagesResponse":
        # Verify the protocol header response type
        header = Header.unpack(data)
        assert ResponseType(header.header_type) == ResponseType.READ_MESSAGES

        return ReadMessagesResponse()
