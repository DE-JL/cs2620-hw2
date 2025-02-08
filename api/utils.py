import socket

from entity.header import *
from .get_messages import GetMessagesRequest
from .authenticate import AuthRequest
from .send_message import SendMessageRequest
from .delete_message import DeleteMessageRequest
from .list_users import ListUsersRequest


def parse_request(header: Header, data: bytes):
    request_type = RequestType(header.header_type)
    match request_type:
        case RequestType.DEBUG:
            return None
        case RequestType.AUTHENTICATE:
            return AuthRequest.unpack(data)
        case RequestType.GET_MESSAGES:
            return GetMessagesRequest.unpack(data)
        case RequestType.SEND_MESSAGE:
            return SendMessageRequest.unpack(data)
        case RequestType.DELETE_MESSAGE:
            return DeleteMessageRequest.unpack(data)
        case RequestType.LIST_USERS:
            return ListUsersRequest.unpack(data)


def send_str(sock: socket.socket, s: str):
    """
    A utility function that wires a string (for logging).
    :param sock: Target socket.
    :param s: The string to send.
    """
    s_bytes = s.encode("utf-8")
    header = Header(RequestType.DEBUG.value, len(s_bytes))
    sock.sendall(header.pack() + s_bytes)
