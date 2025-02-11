import struct

from pydantic import BaseModel

from config import PROTOCOL_TYPE
from entity import *


class SendMessageRequest(BaseModel):
    """
    Send message request.
    :var message: Message object.
    """
    username: str
    message: Message

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")

            # Pack the data
            pack_format = f"!I {len(self.username)}s"
            data = struct.pack(pack_format, len(username_bytes), username_bytes)
            data += self.message.pack()

            # Prepend the protocol header
            header = Header(header_type=RequestType.SEND_MESSAGE.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=RequestType.SEND_MESSAGE.value,
                            payload_size=len(data))
            return header.pack() + data

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

            return SendMessageRequest(username=username,
                                      message=message)
        else:
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.SEND_MESSAGE
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return SendMessageRequest.model_validate_json(json_str)


class SendMessageResponse(BaseModel):
    """
    Send message response.
    """

    @staticmethod
    def pack() -> bytes:
        return Header(header_type=ResponseType.SEND_MESSAGE.value).pack()

    @staticmethod
    def unpack(data: bytes) -> "SendMessageResponse":
        # Verify the protocol header response type
        header = Header.unpack(data)
        assert ResponseType(header.header_type) == ResponseType.SEND_MESSAGE

        return SendMessageResponse()
