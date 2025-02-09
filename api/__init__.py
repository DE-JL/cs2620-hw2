from .authenticate import AuthRequest
from .delete_user import DeleteUserRequest
from .get_messages import GetMessagesRequest, GetMessagesResponse
from .list_users import ListUsersRequest, ListUsersResponse
from .send_message import SendMessageRequest
from .read_messages import ReadMessagesRequest
from .delete_messages import DeleteMessagesRequest
from .delete_user import DeleteUserRequest
from .utils import send_str

Request = (AuthRequest |
           GetMessagesRequest |
           ListUsersRequest |
           SendMessageRequest |
           ReadMessagesRequest |
           DeleteMessagesRequest |
           DeleteUserRequest)

__all__ = [
    "Request",
    "AuthRequest",
    "GetMessagesRequest", "GetMessagesResponse",
    "ListUsersRequest", "ListUsersResponse",
    "SendMessageRequest",
    "ReadMessagesRequest",
    "DeleteMessagesRequest",
    "DeleteUserRequest",
    "send_str",
]
