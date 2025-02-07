import struct
import json

class JsonBody:
    def __init__(self, body: str):
        self.body = body

    def pack(self):
        body_bytes = self.body.encode("utf-8")

        # Pack the bytes together
        pack_format = f"!I {len(body_bytes)}s"
        return struct.pack(pack_format, len(body_bytes), body_bytes)

    @staticmethod
    def unpack(bytestream: bytes):
        # Unpack the header
        header_format = "!I"
        header_size = struct.calcsize(header_format)
        body_len = struct.unpack(header_format, bytestream[:header_size])[0]

        # Unpack body
        data_format = f"!{body_len}s"
        body_bytes = struct.unpack(data_format, bytestream[header_size:])

        # Decode body
        body = body_bytes.decode("utf-8")

        return JsonBody(body)
    
    def get_body_dict(self):
        return json.loads(self.body)
    
    @staticmethod
    def from_dict(body_dict):
        return JsonBody(json.dumps(body_dict))
