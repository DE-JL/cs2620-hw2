from entity.header import *
from entity import Message


class SendMessageRequest:
    """
    Send message request.
    :var message: Message object.
    """

    def __init__(self, message: Message):
        self.message = message

    def __str__(self):
        return f"SendMessageRequest({self.message})"

    def pack(self):
        if PROTOCOL_TYPE != "json":
            # Pack the message
            data = self.message.pack()

            # Prepend the header
            header = Header(RequestType.SEND_MESSAGE.value, len(data))
            return header.pack() + data
        else:
            # Encode the JSON object
            # obj = {
            #     "sender": self.sender,
            #     "receiver": self.receiver,
            #     "body": self.body,
            #     "message_id": str(self.message_id),
            #     "timestamp": self.timestamp
            # }
            # obj_str = json.dumps(obj)
            # obj_bytes = obj_str.encode("utf-8")
            #
            # # Prepend the header
            # header = Header(RequestType.SEND_MESSAGE.value, len(obj_bytes))
            # return header.pack() + obj_bytes
            # TODO
            raise Exception("json not implemented yet")

    @staticmethod
    def unpack(data: bytes):
        if PROTOCOL_TYPE != "json":
            # Unpack the header
            Header.unpack(data)
            data = data[Header.SIZE:]

            # Unpack the message
            message = Message.unpack(data)

            return SendMessageRequest(message)
        else:
            # Decode and load the JSON object
            # obj_str = data.decode("utf-8")
            # obj = json.loads(obj_str)
            # print(obj)
            #
            # return SendMessageRequest(obj["sender"],
            #                           obj["receiver"],
            #                           obj["body"],
            #                           uuid.UUID(obj["message_id"]),
            #                           obj["timestamp"])
            # TODO
            raise Exception("json not implemented yet")
