from api import *
from entity import RequestType


def parse_request(request_type: RequestType, data: bytes):
    match request_type:
        case RequestType.ECHO:
            return None
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
