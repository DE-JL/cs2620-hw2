from pydantic import BaseModel

from .header import Header, ResponseType
from config import PROTOCOL_TYPE


class ErrorResponse(BaseModel):
    message: str

    def pack(self) -> bytes:
        """
        Serialization format:
            <MESSAGE_LEN> <MESSAGE>
        """
        if PROTOCOL_TYPE != "json":
            # Pack the data
            data = self.message.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=ResponseType.ERROR.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=ResponseType.ERROR.value,
                            payload_size=len(data))
            return header.pack() + data

    @staticmethod
    def unpack(data: bytes) -> "ErrorResponse":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.ERROR
            data = data[Header.SIZE:]

            # Decode the message
            message = data.decode("utf-8")

            return ErrorResponse(message=message)
        else:
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.ERROR
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return ErrorResponse.model_validate_json(json_str)
