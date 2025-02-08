import json

from entity.header import *


class AuthRequest:
    """
    Authenticate request.
    :type Auth.ActionType: An enum for the types of possible authentication actions.
    :var action_type: The realized action type.
    :var username: The username of the user attempting to authenticate.
    :var password: The password of the user attempting to authenticate.
    """

    class ActionType(Enum):
        CREATE_ACCOUNT = 0
        LOGIN = 1

    def __init__(self, action_type: ActionType, username: str, password: str):
        self.action_type = action_type
        self.username = username
        self.password = password

    def __str__(self):
        return f"AuthRequest({self.action_type}, {self.username}, {self.password})"

    def pack(self):
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

            # Prepend the header
            header = Header(RequestType.AUTHENTICATE.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "action_type": self.action_type.value,
                "username": self.username,
                "password": self.password
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = Header(RequestType.AUTHENTICATE.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!B I I"
            action_type_value, username_len, password_len = struct.unpack_from(header_format, data)
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{username_len}s {password_len}s"
            username_bytes, password_bytes = struct.unpack_from(data_format, data)

            # Decode the data
            username = username_bytes.decode("utf-8")
            password = password_bytes.decode("utf-8")

            return AuthRequest(AuthRequest.ActionType(action_type_value),
                               username,
                               password)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)

            return AuthRequest(AuthRequest.ActionType(obj["action_type"]),
                               obj["username"],
                               obj["password"])
