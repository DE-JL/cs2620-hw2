from pydantic import BaseModel, Field
import time
import uuid

from .header import *


class Message(BaseModel):
    sender: str
    receiver: str
    body: str
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    ts: float = Field(default_factory=time.time)
    read: bool = False

    def pack(self) -> bytes:
        if PROTOCOL_TYPE != "json":
            # Encode the data
            sender_bytes = self.sender.encode("utf-8")
            receiver_bytes = self.receiver.encode("utf-8")
            body_bytes = self.body.encode("utf-8")
            message_id_bytes = self.message_id.bytes

            # Pack the data
            pack_format = f"!I I I {len(sender_bytes)}s {len(receiver_bytes)}s {len(body_bytes)}s 16s d ?"
            data = struct.pack(pack_format,
                               len(sender_bytes), len(receiver_bytes), len(body_bytes),
                               sender_bytes, receiver_bytes, body_bytes,
                               message_id_bytes,
                               self.ts,
                               self.read)

            # Prepend the header
            header = Header(0, len(data))
            return header.pack() + data
        else:
            # TODO
            pass

    @staticmethod
    def unpack(data: bytes) -> "Message":
        if PROTOCOL_TYPE != "json":
            # Unpack the header
            header_format = f"!I I I"
            sender_len, receiver_len, body_len = struct.unpack_from(header_format, data)
            data = data[struct.calcsize(header_format):]

            print(sender_len, receiver_len, body_len)

            # Unpack the data
            data_format = f"!{sender_len}s {receiver_len}s {body_len}s 16s d ?"
            (sender_bytes, receiver_bytes, body_bytes, message_id_bytes,
             ts, read) = struct.unpack_from(data_format, data)

            # Decode the data
            sender = sender_bytes.decode("utf-8")
            receiver = receiver_bytes.decode("utf-8")
            body = body_bytes.decode("utf-8")
            message_id = uuid.UUID(bytes=message_id_bytes)

            return Message(sender=sender,
                           receiver=receiver,
                           body=body,
                           message_id=message_id,
                           ts=ts,
                           read=read)
        else:
            # TODO
            pass
