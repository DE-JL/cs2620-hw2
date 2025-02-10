import netifaces

from api import *
from entity import RequestType


def get_ipaddr():
    try:
        addrs = netifaces.ifaddresses("en0")

        # netifaces.AF_INET is the IPv4 family
        if netifaces.AF_INET in addrs:
            # Each entry looks like {'addr': '10.250.49.49', 'netmask': '255.255.0.0', 'broadcast': '10.250.255.255'}
            return addrs[netifaces.AF_INET][0]['addr']
    except ValueError:
        # 'en0' might not exist on this machine
        return None


def parse_request(request_type: RequestType, data: bytes):
    match request_type:
        case RequestType.ECHO:
            return EchoRequest.unpack(data)
        case RequestType.AUTHENTICATE:
            return AuthRequest.unpack(data)
        case RequestType.GET_MESSAGES:
            return GetMessagesRequest.unpack(data)
        case RequestType.LIST_USERS:
            return ListUsersRequest.unpack(data)
        case RequestType.SEND_MESSAGE:
            return SendMessageRequest.unpack(data)
        case RequestType.READ_MESSAGES:
            return ReadMessagesRequest.unpack(data)
        case RequestType.DELETE_MESSAGES:
            return DeleteMessagesRequest.unpack(data)
        case RequestType.DELETE_USER:
            return DeleteUserRequest.unpack(data)
        case _:
            print("Unknown request type.")
            exit(1)
