import json

from .header import Header, ResponseType


class ErrorResponse:
    """
    Error response.
    :var message: The descriptive error message.
    """

    def __init__(self, message: str):
        self.message = message

    def __eq__(self, other):
        return self.message == other.message

    def __str__(self):
        return f"ErrorResponse({self.message})"

    def pack(self) -> bytes:
        # Pack the data
        data = self.message.encode("utf-8")

        # Prepend the protocol header
        header = Header(ResponseType.ERROR.value, len(data))
        return header.pack() + data

    @staticmethod
    def unpack(data: bytes) -> "ErrorResponse":
        # Verify the protocol header response type
        header = Header.unpack(data)
        assert ResponseType(header.header_type) == ResponseType.ERROR
        data = data[Header.SIZE:]

        # Decode the message
        message = data.decode("utf-8")

        return ErrorResponse(message)
