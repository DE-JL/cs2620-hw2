import struct

from pydantic import BaseModel

from .utils import pack_strings, unpack_strings
from config import PROTOCOL_TYPE
from entity import *


class ListUsersRequest(BaseModel):
    """
    List users request.
    :var username: The username of the user requesting accounts matching pattern.
    :var pattern: The regex pattern to match.
    """
    username: str
    pattern: str

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")
            pattern_bytes = self.pattern.encode("utf-8")

            # Pack the data
            pack_format = f"!I I {len(username_bytes)}s {len(pattern_bytes)}s"
            data = struct.pack(pack_format,
                               len(username_bytes), len(pattern_bytes),
                               username_bytes, pattern_bytes)

            # Prepend the protocol header
            header = Header(header_type=RequestType.LIST_USERS.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=RequestType.LIST_USERS.value,
                            payload_size=len(data))
            return header.pack() + data

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.LIST_USERS
            data = data[Header.SIZE:]

            # Unpack the data header
            header_format = "!I I"
            username_len, pattern_len = struct.unpack_from(header_format, data)
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{username_len}s {pattern_len}s"
            username_bytes, pattern_bytes = struct.unpack_from(data_format, data)

            # Decode the data
            username = username_bytes.decode("utf-8")
            pattern = pattern_bytes.decode("utf-8")

            return ListUsersRequest(username=username,
                                    pattern=pattern)
        else:
            # Verify the protocol header request type
            header = Header.unpack(data)
            assert RequestType(header.header_type) == RequestType.LIST_USERS
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return ListUsersRequest.model_validate_json(json_str)


class ListUsersResponse(BaseModel):
    """
    List users response.
    :var usernames: The list of users matching the pattern.
    """
    usernames: list[str]

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Pack the data
            data = pack_strings(self.usernames)

            # Prepend the protocol header
            header = Header(header_type=ResponseType.LIST_USERS.value,
                            payload_size=len(data))
            return header.pack() + data
        else:
            # Encode the data
            json_str = self.model_dump_json()
            data = json_str.encode("utf-8")

            # Prepend the protocol header
            header = Header(header_type=ResponseType.LIST_USERS.value,
                            payload_size=len(data))
            return header.pack() + data

    @staticmethod
    def unpack(data: bytes) -> "ListUsersResponse":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.LIST_USERS
            data = data[Header.SIZE:]

            # Unpack the usernames
            usernames = unpack_strings(data)

            return ListUsersResponse(usernames=usernames)
        else:
            # Verify the protocol header response type
            header = Header.unpack(data)
            assert ResponseType(header.header_type) == ResponseType.LIST_USERS
            data = data[Header.SIZE:]

            # Decode the data
            json_str = data.decode("utf-8")

            return ListUsersResponse.model_validate_json(json_str)
