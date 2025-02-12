import struct

from enum import Enum
from pydantic import BaseModel, Field

from config import PROTOCOL_TYPE
from entity import *


class AuthRequest(BaseModel):
    class ActionType(Enum):
        CREATE_ACCOUNT = 0
        LOGIN = 1

    action_type: ActionType
    username: str
    password: str

    def pack(self):
        """
        Serialization format:
            <HEADER> <USERNAME_LEN> <PASSWORD_LEN> <USERNAME_BYTES> <PASSWORD_BYTES>
        """
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")
            password_bytes = self.password.encode("utf-8")

            # Pack the data
            pack_format = f"!B I I {len(username_bytes)}s {len(password_bytes)}s"
            data = struct.pack(pack_format,
                               self.action_type.value,
                               len(username_bytes), len(password_bytes),
                               username_bytes, password_bytes)

            # Prepend the protocol header
            header = Header(header_type=RequestType.AUTHENTICATE.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=RequestType.AUTHENTICATE.value,
                            payload_size=len(data))
            return header.pack() + data

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.AUTHENTICATE
            data = data[Header.SIZE:]

            # Unpack the data header
            header_format = "!B I I"
            action_type_value, username_len, password_len = struct.unpack_from(header_format, data)
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{username_len}s {password_len}s"
            username_bytes, password_bytes = struct.unpack_from(data_format, data)

            # Decode the data
            username = username_bytes.decode("utf-8")
            password = password_bytes.decode("utf-8")

            return AuthRequest(action_type=AuthRequest.ActionType(action_type_value),
                               username=username,
                               password=password)
        else:
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.AUTHENTICATE
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return AuthRequest.model_validate_json(json_str)


class AuthResponse(BaseModel):
    """
    Authenticate response.
    """

    @staticmethod
    def pack() -> bytes:
        return Header(header_type=ResponseType.AUTHENTICATE.value).pack()

    @staticmethod
    def unpack(data: bytes) -> "AuthResponse":
        # Verify the protocol header response type
        header = Header.unpack(data)
        assert ResponseType(header.header_type) == ResponseType.AUTHENTICATE

        return AuthResponse()
