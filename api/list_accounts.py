import json

from entity.header import *


class ListAccountsRequest:
    """
    List accounts request.
    :var username: The username of the user requesting accounts matching pattern.
    :var pattern: The regex pattern to match.
    """

    def __init__(self, username: str, pattern: str):
        self.username = username
        self.pattern = pattern

    def __str__(self):
        return f"ListAccounts({self.username}, {self.pattern})"

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

            # Prepend the header
            header = Header(RequestType.LIST_ACCOUNTS.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "username": self.username,
                "pattern": self.pattern
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = Header(RequestType.LIST_ACCOUNTS.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!I I"
            username_len, pattern_len = struct.unpack_from(header_format, data)
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{username_len}s {pattern_len}s"
            username_bytes, pattern_bytes = struct.unpack_from(data_format, data)

            # Decode the data
            username = username_bytes.decode("utf-8")
            pattern = pattern_bytes.decode("utf-8")

            return ListAccountsRequest(username, pattern)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)

            return ListAccountsRequest(obj["username"],
                                       obj["pattern"])
