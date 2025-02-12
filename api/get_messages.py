import struct

from pydantic import BaseModel

from .utils import pack_messages, unpack_messages
from config import PROTOCOL_TYPE
from entity import *


class GetMessagesRequest(BaseModel):
    username: str

    def pack(self):
        """
        Serialization format:
            <HEADER> <USERNAME_LEN> <USERNAME_BYTES> <LIST[MESSAGE_ID]>
        """
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")

            # Pack the data
            pack_format = f"!I {len(self.username)}s"
            data = struct.pack(pack_format, len(username_bytes), username_bytes)

            # Prepend the protocol header
            header = Header(header_type=RequestType.GET_MESSAGES.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=RequestType.GET_MESSAGES.value,
                            payload_size=len(data))
            return header.pack() + data

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.GET_MESSAGES
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

            return GetMessagesRequest(username=username)
        else:
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.GET_MESSAGES
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return GetMessagesRequest.model_validate_json(json_str)


class GetMessagesResponse(BaseModel):
    messages: list[Message]

    def pack(self) -> bytes:
        """
        Serialization format:
            <HEADER> <LIST[MESSAGE]>
        """
        if PROTOCOL_TYPE != "json":
            # Pack the data
            data = pack_messages(self.messages)

            # Prepend the protocol header
            header = Header(header_type=ResponseType.GET_MESSAGES.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=ResponseType.GET_MESSAGES.value,
                            payload_size=len(data))
            return header.pack() + data

    @staticmethod
    def unpack(data: bytes) -> "GetMessagesResponse":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.GET_MESSAGES
            data = data[Header.SIZE:]

            # Unpack the messages
            messages = unpack_messages(data)

            return GetMessagesResponse(messages=messages)
        else:
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.GET_MESSAGES
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return GetMessagesResponse.model_validate_json(json_str)
