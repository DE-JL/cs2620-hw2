import json

from entity.header import *


class ListUsersRequest:
    """
    List users request.
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
            header = Header(RequestType.LIST_USERS.value, len(data))
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
            header = Header(RequestType.LIST_USERS.value, len(obj_bytes))
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

            return ListUsersRequest(username, pattern)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)

            return ListUsersRequest(obj["username"],
                                    obj["pattern"])


class ListUsersResponse:
    """
    List users response.
    :var usernames: The list of users matching the pattern.
    """

    def __init__(self, usernames: list[str]):
        self.usernames = usernames

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Pack the number of usernames
            pack_format = "!I"
            data = struct.pack(pack_format, len(self.usernames))

            # Pack the usernames one by one
            for username in self.usernames:
                username_bytes = username.encode("utf-8")
                data += struct.pack("!I", len(username_bytes))
                data += struct.pack(f"!{len(username_bytes)}s", username_bytes)

            # Prepend the header
            header = Header(ResponseType.LIST_USERS.value, len(data))
            return header.pack() + data
        else:
            # TODO
            raise Exception("json not yet implemented")

    @staticmethod
    def unpack(data: bytes) -> "ListUsersResponse":
        if PROTOCOL_TYPE != "json":
            usernames = []

            # First unpack the number of usernames
            num_usernames = struct.unpack_from("!I", data)[0]
            data = data[struct.calcsize("!I"):]

            for _ in range(num_usernames):
                # Unpack the username bytes len
                username_bytes_len = struct.unpack_from("!I", data)[0]
                data = data[struct.calcsize("!I"):]

                # Unpack, decode, and append the username
                username_bytes = struct.unpack_from(f"!{username_bytes_len}s", data)[0]
                username = username_bytes.decode("utf-8")
                usernames.append(username)
                data = data[struct.calcsize(f"!{username_bytes_len}s"):]

            return ListUsersResponse(usernames)
        else:
            # TODO
            raise Exception("json not implemented yet")
