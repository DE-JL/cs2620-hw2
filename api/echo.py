from entity import *


class EchoRequest:
    """
    Echo request.
    :var string: The echo request string.
    """

    def __init__(self, string: str):
        self.string = string

    def __eq__(self, other):
        return self.string == other.string

    def __str__(self):
        return f"EchoRequest({self.string})"

    def pack(self) -> bytes:
        # Encode the data
        data = self.string.encode("utf-8")

        # Prepend the protocol header
        header = Header(RequestType.ECHO.value, len(data))
        return header.pack() + data

    @staticmethod
    def unpack(data: bytes) -> "EchoRequest":
        # Verify the protocol header request type
        header = Header.unpack(data)
        assert RequestType(header.header_type) == RequestType.ECHO
        data = data[Header.SIZE:]

        # Decode the data
        string = data.decode("utf-8")

        return EchoRequest(string)


class EchoResponse:
    """
    Echo response.
    :var string: The echo response string.
    """

    def __init__(self, string: str):
        self.string = string

    def __eq__(self, other):
        return self.string == other.string

    def __str__(self):
        return f"EchoRequest({self.string})"

    def pack(self) -> bytes:
        # Encode the data
        data = self.string.encode("utf-8")

        # Prepend the protocol header
        header = Header(ResponseType.ECHO.value, len(data))
        return header.pack() + data

    @staticmethod
    def unpack(data: bytes) -> "EchoRequest":
        # Verify the protocol header request type
        header = Header.unpack(data)
        assert ResponseType(header.header_type) == ResponseType.ECHO
        data = data[Header.SIZE:]

        # Decode the data
        string = data.decode("utf-8")

        return EchoRequest(string)
