from .authenticate import AuthRequest
from .get_messages import GetMessagesRequest, GetMessagesResponse
from .read_messages import ReadMessagesRequest
from .send_message import SendMessageRequest
from .delete_message import DeleteMessageRequest
from .list_users import ListUsersRequest, ListUsersResponse
from .utils import parse_request, send_str

Request = (AuthRequest |
           GetMessagesRequest |
           ReadMessagesRequest |
           SendMessageRequest |
           DeleteMessageRequest |
           ListUsersRequest)

__all__ = [
    "Request",
    "AuthRequest",
    "GetMessagesRequest", "GetMessagesResponse",
    "ReadMessagesRequest",
    "SendMessageRequest",
    "DeleteMessageRequest",
    "ListUsersRequest", "ListUsersResponse",
    "parse_request", "send_str",
]
