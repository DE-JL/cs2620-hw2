from .echo import EchoRequest, EchoResponse
from .authenticate import AuthRequest, AuthResponse
from .get_messages import GetMessagesRequest, GetMessagesResponse
from .list_users import ListUsersRequest, ListUsersResponse
from .send_message import SendMessageRequest, SendMessageResponse
from .read_messages import ReadMessagesRequest, ReadMessagesResponse
from .delete_messages import DeleteMessagesRequest, DeleteMessagesResponse
from .delete_user import DeleteUserRequest, DeleteUserResponse

Request = (EchoRequest |
           AuthRequest |
           GetMessagesRequest |
           ListUsersRequest |
           SendMessageRequest |
           ReadMessagesRequest |
           DeleteMessagesRequest |
           DeleteUserRequest)

__all__ = [
    "Request",
    "EchoRequest", "EchoResponse",
    "AuthRequest", "AuthResponse",
    "GetMessagesRequest", "GetMessagesResponse",
    "ListUsersRequest", "ListUsersResponse",
    "SendMessageRequest", "SendMessageResponse",
    "ReadMessagesRequest", "ReadMessagesResponse",
    "DeleteMessagesRequest", "DeleteMessagesResponse",
    "DeleteUserRequest", "DeleteUserResponse",
]
