from .authenticate import AuthRequest
from .get_messages import GetMessagesRequest, GetMessagesResponse
from .read_messages import ReadMessagesRequest
from .send_message import SendMessageRequest
from .delete_message import DeleteMessagesRequest
from .list_users import ListUsersRequest, ListUsersResponse
from .utils import send_str

Request = (AuthRequest |
           GetMessagesRequest |
           ReadMessagesRequest |
           SendMessageRequest |
           DeleteMessagesRequest |
           ListUsersRequest)

__all__ = [
    "Request",
    "AuthRequest",
    "GetMessagesRequest", "GetMessagesResponse",
    "ReadMessagesRequest",
    "SendMessageRequest",
    "DeleteMessagesRequest",
    "ListUsersRequest", "ListUsersResponse",
    "send_str",
]
