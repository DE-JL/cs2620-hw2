from dataclasses import dataclass, field
import struct
import time
import uuid

from .header import DataType, Header
from config import PROTOCOL_TYPE


@dataclass
class Message:
    sender: str
    receiver: str
    body: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    ts: float = field(default_factory=time.time)
    read: bool = field(default=False)

    def set_read(self):
        self.read = True

    def pack(self) -> bytes:
        if PROTOCOL_TYPE != "json":
            # Encode the data
            sender_bytes = self.sender.encode("utf-8")
            receiver_bytes = self.receiver.encode("utf-8")
            body_bytes = self.body.encode("utf-8")
            id_bytes = self.id.bytes

            # Pack the data
            pack_format = f"!I I I {len(sender_bytes)}s {len(receiver_bytes)}s {len(body_bytes)}s 16s d ?"
            data = struct.pack(pack_format,
                               len(sender_bytes), len(receiver_bytes), len(body_bytes),
                               sender_bytes, receiver_bytes, body_bytes,
                               id_bytes,
                               self.ts,
                               self.read)

            # Prepend the protocol header
            header = Header(DataType.MESSAGE.value)
            return header.pack() + data
        else:
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes) -> "Message":
        if PROTOCOL_TYPE != "json":
            # Verify the protocol header data type
            header = Header.unpack(data)
            assert DataType(header.header_type) == DataType.MESSAGE
            data = data[Header.SIZE:]

            # Unpack the message header
            header_format = "!I I I"
            sender_len, receiver_len, body_len = struct.unpack_from(header_format, data)
            data = data[struct.calcsize(header_format):]

            # Unpack the data
            data_format = f"!{sender_len}s {receiver_len}s {body_len}s 16s d ?"
            sender_bytes, receiver_bytes, body_bytes, id_bytes, ts, read = struct.unpack_from(data_format, data)

            # Decode the data
            sender = sender_bytes.decode("utf-8")
            receiver = receiver_bytes.decode("utf-8")
            body = body_bytes.decode("utf-8")
            message_id = uuid.UUID(bytes=id_bytes)

            return Message(sender=sender,
                           receiver=receiver,
                           body=body,
                           id=message_id,
                           ts=ts,
                           read=read)
        else:
            # TODO
            raise Exception("json not implemented yet")
