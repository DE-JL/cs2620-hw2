import json
import uuid

from entity.header import *


class SendMessageRequest:
    """
    Send message request.
    :var sender: The username of the sender.
    :var receiver: The username of the recipient.
    :var message_id: The id of the message.
    :var body: The body (text) of the message.
    :var timestamp: The timestamp of the message.
    """

    def __init__(self, sender: str, receiver: str, body: str, message_id: uuid.UUID, timestamp: float):
        self.sender = sender
        self.receiver = receiver
        self.body = body
        self.message_id = message_id
        self.timestamp = timestamp

    def __str__(self):
        return (f"SendMessage({self.sender}, {self.receiver}, {self.body},"
                f" {self.message_id}, {self.timestamp})")

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Encode the data
            sender_bytes = self.sender.encode("utf-8")
            receiver_bytes = self.receiver.encode("utf-8")
            body_bytes = self.body.encode("utf-8")
            message_id_bytes = self.message_id.bytes

            # Pack the data
            pack_format = f"!I I I {len(sender_bytes)}s {len(receiver_bytes)}s {len(body_bytes)}s 16s d"
            data = struct.pack(pack_format,
                               len(sender_bytes), len(receiver_bytes), len(body_bytes),
                               sender_bytes, receiver_bytes, body_bytes,
                               message_id_bytes, self.timestamp)

            # Prepend the header
            header = Header(RequestType.SEND_MESSAGE.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            obj = {
                "sender": self.sender,
                "receiver": self.receiver,
                "body": self.body,
                "message_id": str(self.message_id),
                "timestamp": self.timestamp
            }
            obj_str = json.dumps(obj)
            obj_bytes = obj_str.encode("utf-8")

            # Prepend the header
            header = Header(RequestType.SEND_MESSAGE.value, len(obj_bytes))
            return header.pack() + obj_bytes

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = "!I I I"
            sender_len, receiver_len, body_len = struct.unpack_from(header_format, data)
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{sender_len}s {receiver_len}s {body_len}s 16s d"
            sender_bytes, receiver_bytes, body_bytes, message_id_bytes, timestamp = struct.unpack(data_format, data)

            # Decode the data
            sender = sender_bytes.decode("utf-8")
            receiver = receiver_bytes.decode("utf-8")
            body = body_bytes.decode("utf-8")
            message_id = uuid.UUID(bytes=message_id_bytes)

            return SendMessageRequest(sender, receiver, body, message_id, timestamp)
        else:
            # Decode and load the JSON object
            obj_str = data.decode("utf-8")
            obj = json.loads(obj_str)
            print(obj)

            return SendMessageRequest(obj["sender"],
                                      obj["receiver"],
                                      obj["body"],
                                      uuid.UUID(obj["message_id"]),
                                      obj["timestamp"])
