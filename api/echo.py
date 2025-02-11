from pydantic import BaseModel

from config import PROTOCOL_TYPE
from entity import *


class EchoRequest(BaseModel):
    """
    Echo request.
    :var string: The echo request string.
    """
    string: str

    def pack(self) -> bytes:
        if PROTOCOL_TYPE != "json":
            # Encode the data
            data = self.string.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=RequestType.ECHO.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=RequestType.ECHO.value,
                            payload_size=len(data))
            return header.pack() + data

    @staticmethod
    def unpack(data: bytes) -> "EchoRequest":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.ECHO
            data = data[Header.SIZE:]

            # Decode the data
            string = data.decode("utf-8")

            return EchoRequest(string=string)
        else:
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.ECHO
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return EchoRequest.model_validate_json(json_str)


class EchoResponse(BaseModel):
    """
    Echo response.
    :var string: The echo response string.
    """
    string: str

    def pack(self) -> bytes:
        if PROTOCOL_TYPE != "json":
            # Encode the data
            data = self.string.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=ResponseType.ECHO.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=ResponseType.ECHO.value,
                            payload_size=len(data))
            return header.pack() + data

    @staticmethod
    def unpack(data: bytes) -> "EchoResponse":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.ECHO
            data = data[Header.SIZE:]

            # Decode the data
            string = data.decode("utf-8")

            return EchoResponse(string=string)
        else:
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.ECHO
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return EchoResponse.model_validate_json(json_str)
