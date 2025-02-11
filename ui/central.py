from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QFrame

from .send_message import SendMessage
from .list_account import ListAccount


class Central(QWidget):
    def __init__(self):
        super().__init__()
        self.send_message = SendMessage()
        self.list_account = ListAccount()

        self.frame_layout = QHBoxLayout()

        self.frame_layout.addWidget(self.send_message)
        self.frame_layout.addWidget(self.list_account)

        self.frame = QFrame()
        self.setLayout(self.frame_layout)
