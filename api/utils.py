import socket
import struct
import uuid

from entity import *


def send_str(sock: socket.socket, s: str):
    """
    A utility function that wires a string (for logging).
    :param sock: Target socket.
    :param s: The string to send.
    """
    s_bytes = s.encode("utf-8")
    header = Header(RequestType.ECHO.value, len(s_bytes))
    sock.sendall(header.pack() + s_bytes)


def pack_messages(messages: list[Message]) -> bytes:
    # Pack the length
    data = struct.pack("!I", len(messages))

    # Pack the messages one by one
    for message in messages:
        message_bytes = message.pack()
        data += struct.pack("!I", len(message_bytes))
        data += message_bytes

    # Prepend the protocol header
    header = Header(DataType.LIST.value, len(data))
    return header.pack() + data


def unpack_messages(data: bytes) -> list[Message]:
    # Verify the protocol header data type
    header = Header.unpack(data)
    assert DataType(header.header_type) == DataType.LIST
    data = data[Header.SIZE:]

    # Unpack the number of messages
    num_messages = struct.unpack_from("!I", data)[0]
    data = data[struct.calcsize("!I"):]

    # Unpack the messages one by one
    messages = []
    for _ in range(num_messages):
        # Unpack the message size
        message_size = struct.unpack_from("!I", data)[0]
        data = data[struct.calcsize("!I"):]

        # Unpack the message
        message = Message.unpack(data)
        data = data[message_size:]

        # Append to the list
        messages.append(message)

    return messages


def pack_strings(strings: list[str]) -> bytes:
    # Pack the length
    data = struct.pack("!I", len(strings))

    # Pack the strings one by one
    for string in strings:
        string_bytes = string.encode("utf-8")
        data += struct.pack("!I", len(string_bytes))
        data += string_bytes

    # Prepend the protocol header
    header = Header(DataType.LIST.value, len(data))
    return header.pack() + data


def unpack_strings(data: bytes) -> list[str]:
    # Verify the protocol header data type
    header = Header.unpack(data)
    assert DataType(header.header_type) == DataType.LIST
    data = data[Header.SIZE:]

    # Unpack the number of strings
    num_strings = struct.unpack_from("!I", data)[0]
    data = data[struct.calcsize("!I"):]

    # Unpack the strings one by one
    strings = []
    for _ in range(num_strings):
        # Unpack the string size
        string_len = struct.unpack_from("!I", data)[0]
        data = data[struct.calcsize("!I"):]

        # Unpack the string
        string_bytes = struct.unpack_from(f"!{string_len}s", data)[0]
        string = string_bytes.decode("utf-8")
        data = data[string_len:]

        # Append to the list
        strings.append(string)

    return strings


def pack_uuids(uuids: list[uuid.UUID]) -> bytes:
    # Pack the length
    data = struct.pack("!I", len(uuids))

    # Pack the UUIDs one by one
    for uid in uuids:
        data += struct.pack("!16s", uid.bytes)

    # Prepend the protocol header
    header = Header(DataType.LIST.value, len(data))
    return header.pack() + data


def unpack_uuids(data: bytes) -> list[uuid.UUID]:
    # Verify the protocol header data type
    header = Header.unpack(data)
    assert DataType(header.header_type) == DataType.LIST
    data = data[Header.SIZE:]

    # Unpack the number of UUIDs
    num_uuids = struct.unpack_from("!I", data)[0]
    data = data[struct.calcsize("!I"):]

    # Unpack the UUIDs one by one
    uuids = []
    for _ in range(num_uuids):
        # Unpack the UUID
        uuid_bytes = struct.unpack_from("!16s", data)[0]
        uid = uuid.UUID(bytes=uuid_bytes)
        data = data[struct.calcsize("!16s"):]

        # Append to the list
        uuids.append(uid)

    return uuids
