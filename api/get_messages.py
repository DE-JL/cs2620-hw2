import json

from entity import Message
from entity.header import *


class GetMessagesRequest:
    """
    Get messages request.
    :var username: The username to get messages for.
    """

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f"GetMessagesRequest({self.username})"

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Encode the data
            username_bytes = self.username.encode("utf-8")

            # Pack the data
            pack_format = f"!I {len(self.username)}s"
            data = struct.pack(pack_format, len(username_bytes), username_bytes)

            # Prepend the header
            header = Header(RequestType.GET_MESSAGES.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "username": self.username,
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = Header(RequestType.GET_MESSAGES.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!I"
            username_len = struct.unpack_from(header_format, data)[0]
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{username_len}s"
            username_bytes = struct.unpack_from(data_format, data)[0]

            # Decode the data
            username = username_bytes.decode("utf-8")

            return GetMessagesRequest(username)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)

            return GetMessagesRequest(obj["username"])


class GetMessagesResponse:
    """
    Get messages response.
    :var messages: The messages retrieved
    """

    def __init__(self, messages: list[Message]):
        self.messages = messages

    def __str__(self):
        return f"GetMessagesResponse({self.messages})"

    def pack(self) -> bytes:
        if PROTOCOL_TYPE != "json":
            # Pack the data
            pack_format = "!I"
            data = struct.pack(pack_format, len(self.messages))

            # Pack all messages sequentially
            for message in self.messages:
                data += message.pack()

            # Prepend the header
            header = Header(ResponseType.GET_MESSAGES.value, len(data))
            return header.pack() + data
        else:
            # TODO
            pass

    @staticmethod
    def unpack(data: bytes) -> "GetMessagesResponse":
        if PROTOCOL_TYPE != "json":
            messages = []

            # First determine the number of messages
            num_messages_format = "!I"
            num_messages = struct.unpack_from(num_messages_format, data)[0]
            data = data[struct.calcsize(num_messages_format):]

            print(f"num_messages: {num_messages}")

            # Process messages one by one
            for _ in range(num_messages):
                # Read how long the message is
                message_size_header = Header.unpack(data)
                message_size = message_size_header.payload_size
                data = data[Header.SIZE:]

                print(f"message_size: {message_size}")

                # Read and append the message
                message = Message.unpack(data)
                messages.append(message)
                data = data[message_size:]

            return GetMessagesResponse(messages)
        else:
            # TODO
            pass
