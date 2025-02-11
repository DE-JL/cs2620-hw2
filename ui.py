import socket
import sys
import argparse
from sys import argv
import time
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QListWidget, QWidget, QListWidgetItem
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QDesktopWidget, QHBoxLayout, QAbstractItemView
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIntValidator, QValidator
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QMessageBox, QLineEdit, QTextEdit
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtCore import QThread



from config import HOST, PORT
from entity import Message, ResponseType, Header, ErrorResponse

from utils import recv_resp_bytes

import api

import hashlib

SAMPLE_DATA = [
    Message(sender="alice", receiver="bob", body="Hey Bob, are you free later?"),
    Message(sender="charlie", receiver="bob", body="Bob, I sent you the report."),
    Message(sender="dave", receiver="bob", body="Let's meet at 5 PM."),
    Message(sender="eve", receiver="bob", body="Check your email when you can."),
    Message(sender="frank", receiver="bob", body="Want to grab lunch today?", read=True),
    Message(sender="george", receiver="bob", body="I need help with my project."),
    Message(sender="harry", receiver="bob", body="Hey, got time for a quick call?"),
    Message(sender="isaac", receiver="bob", body="Your package has been delivered.", read=True),
    Message(sender="jack", receiver="bob", body="Meeting rescheduled to tomorrow.", read=True),
    Message(sender="kate", receiver="bob", body="Thanks for the help earlier!")
]


class UserSession:
    """
    A class to represent a socket-based user session
    """
    def __init__(self, host, port, main_frame, window, debug=False):
        self.main_frame = main_frame
        self.window = window
        self.debug = debug
        self.username = None

        self.host = host
        self.port = port

        self.message_thread = None
        self.message_worker = None
        self.messages = None

        # initialize connection for main GUI thread
        if not self.debug:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
            except ConnectionRefusedError:
                print("Connection refused. Please check if the server is running.")
                sys.exit(1)

        # Register event handlers
        self.main_frame.login.login_button.clicked.connect(self.login_user)
        self.main_frame.login.sign_up_button.clicked.connect(self.sign_up)
        self.main_frame.logged_in.sign_out_button.clicked.connect(self.sign_out)
        self.main_frame.logged_in.delete_account_button.clicked.connect(self.delete_account)
        self.main_frame.central.list_account.search_button.clicked.connect(self.list_account_event)
        self.main_frame.central.send_message.send_button.clicked.connect(self.send_message_event)
        self.main_frame.view_messages.read_button.clicked.connect(self.read_messages_event)
        # TODO Add event handler for delete message
        self.main_frame.view_messages.delete_button.clicked.connect(self.delete_messages_event)


    def authenticate_user(self, action):
        print("Authenticating user...")
        username  = self.main_frame.login.user_entry.text()
        password = self.main_frame.login.password_entry.text()

        hashed_password = hash_string(password)
        
        if self.debug and username == "admin" and password == "pass": # Dummy default password
            # hide the login frame
            self.main_frame.login.hide()
            # show logged in frame
            self.main_frame.logged_in.show()
            self.main_frame.central.show()
            self.main_frame.view_messages.show()
            self.main_frame.logged_in.update_user_label(username)
            self.username = username
            return
        elif self.debug:
            QMessageBox.critical(self.window, 'Error', "Authentication failed")
            return
        
        auth_request = api.AuthRequest(action, username, hashed_password)
        self.sock.sendall(auth_request.pack())

        header, recvd = recv_resp_bytes(self.sock)

        if ResponseType(header.header_type) == ResponseType.ERROR:
            resp = ErrorResponse.unpack(recvd)
            QMessageBox.critical(self.window, 'Error', resp.message)
            return
        
        api.AuthResponse.unpack(recvd)
        
        print("Authentication successful")

        # hide the login frame
        self.main_frame.login.hide()
        # show logged in frame
        self.main_frame.logged_in.show()
        self.main_frame.central.show()
        self.main_frame.view_messages.show()
        self.main_frame.logged_in.update_user_label(username)
        self.username = username

        self.start_logged_session()

    def sign_up(self):
        self.authenticate_user(api.AuthRequest.ActionType.CREATE_ACCOUNT)
    
    def login_user(self):
        self.authenticate_user(api.AuthRequest.ActionType.LOGIN)

    def sign_out(self):

        if not self.debug:
            self.stop_logged_session()
        print("Signing out...")
        # hide logged in frame
        self.main_frame.logged_in.hide()
        self.main_frame.central.hide()
        self.main_frame.view_messages.hide()
        # show login frame
        self.main_frame.login.user_entry.setText("")
        self.main_frame.login.password_entry.setText("")
        self.main_frame.login.show()
        self.username = None

    def delete_account(self):
        delete_user_request = api.DeleteUserRequest(self.username)
        self.sock.sendall(delete_user_request.pack())

        header, recvd = recv_resp_bytes(self.sock)

        if ResponseType(header.header_type) == ResponseType.ERROR:
            resp = ErrorResponse.unpack(recvd)
            QMessageBox.critical(self.window, 'Error', resp.message)
            return
        
        api.DeleteUserResponse.unpack(recvd)
        
        print("Account deleted")
        self.sign_out()
    
    def list_account_event(self):
        search_string = self.main_frame.central.list_account.search_entry.text()

        list_account_request = api.ListUsersRequest(self.username, search_string)
        self.sock.sendall(list_account_request.pack())

        header, recvd = recv_resp_bytes(self.sock)

        if ResponseType(header.header_type) == ResponseType.ERROR:
            resp = ErrorResponse.unpack(recvd)
            QMessageBox.critical(self.window, 'Error', resp.message)
            return
        
        list_account_response = api.ListUsersResponse.unpack(recvd)
        
        self.main_frame.central.list_account.account_list.clear()
        for idx, user in enumerate(list_account_response.usernames):
            self.main_frame.central.list_account.account_list.insertItem(idx, user)
    
    def send_message_event(self):
        recipient = self.main_frame.central.send_message.recipient_entry.text()
        message_body = self.main_frame.central.send_message.message_text.toPlainText()

        msg = Message(sender=self.username, receiver=recipient, body=message_body)

        send_message_request = api.SendMessageRequest(self.username, msg)
        self.sock.sendall(send_message_request.pack())

        header, recvd = recv_resp_bytes(self.sock)

        if ResponseType(header.header_type) == ResponseType.ERROR:
            resp = ErrorResponse.unpack(recvd)
            QMessageBox.critical(self.window, 'Error', resp.message)
            return
        
        api.SendMessageResponse.unpack(recvd)

        self.main_frame.central.send_message.recipient_entry.setText("")
        self.main_frame.central.send_message.message_text.setText("")
    
    def handle_new_messages(self, messages):
        self.messages = messages
        self.messages.sort(key = lambda x: x.ts, reverse=True)
        self.main_frame.view_messages.update_message_list(messages)
    
    def delete_messages_event(self):
        selected_items = self.main_frame.view_messages.message_list.selectedItems()
        if not selected_items:
            print("No messages selected")
            return  # Nothing to delete

        ids_to_delete = []
        for item in selected_items:
            # Retrieve the original Message object
            msg = item.data(Qt.UserRole)
            ids_to_delete.append(msg.id)

        delete_messages_request = api.DeleteMessagesRequest(self.username, ids_to_delete)
        self.sock.sendall(delete_messages_request.pack())

        header, recvd = recv_resp_bytes(self.sock)

        if ResponseType(header.header_type) == ResponseType.ERROR:
            resp = ErrorResponse.unpack(recvd)
            QMessageBox.critical(self.window, 'Error', resp.message)
            return
        
        api.DeleteMessagesResponse.unpack(recvd)

    def read_messages_event(self):
        num_to_read = int(self.main_frame.view_messages.num_read_entry.text())

        ids = [message.id for message in self.messages if not message.read]

        num_to_read = min(num_to_read, len(self.messages))

        ids = ids[-num_to_read:]

        # make read message request
        read_messages_request = api.ReadMessagesRequest(self.username, ids)
        self.sock.sendall(read_messages_request.pack())

        header, recvd = recv_resp_bytes(self.sock)

        if ResponseType(header.header_type) == ResponseType.ERROR:
            resp = ErrorResponse.unpack(recvd)
            QMessageBox.critical(self.window, 'Error', resp.message)
            return
        
        api.ReadMessagesResponse.unpack(recvd)


    def start_logged_session(self):
        # Create the worker with a fresh socket
        self.message_worker = MessageUpdaterWorker(
            host=self.host,
            port=self.port,
            username=self.username, 
            update_interval=0.1
        )

        # Create the thread object
        self.message_thread = QThread()
        
        # Move the worker to the thread
        self.message_worker.moveToThread(self.message_thread)
        
        # When the thread starts, run the worker's main loop
        self.message_thread.started.connect(self.message_worker.run)
        
        # Connect the worker's signal to your handler in the main thread
        self.message_worker.messages_received.connect(self.handle_new_messages)
        
        # Start the thread
        self.message_thread.start()

    
    def stop_logged_session(self):
        if self.message_worker and self.message_thread:
            # Signal the worker to stop
            self.message_worker.stop()
            
            # Ask the thread to quit (once run() returns)
            self.message_thread.quit()
            
            # Wait for the thread to fully exit
            self.message_thread.wait()
            
            # Cleanup references
            self.message_worker = None
            self.message_thread = None



class MessageUpdaterWorker(QObject):
    """
    Worker class to periodically fetch new messages
    from a separate socket connection.
    """
    messages_received = pyqtSignal(list)  # emitted when new messages arrive
    
    def __init__(self, host, port, username, update_interval=2, parent=None):
        """
        :param host: Server's hostname or IP address
        :param port: Server's port
        :param username: The current user's name (for message queries, if needed)
        :param update_interval: How often (in seconds) to poll for messages
        """
        super().__init__(parent)
        self.host = host
        self.port = port
        self.username = username
        self.update_interval = update_interval
        self._running = False
        self._sock = None

    @pyqtSlot()
    def run(self):
        """
        Worker thread's main loop.
        1) Create and connect a separate socket
        2) Periodically fetch new messages
        3) Emit results back to main thread
        """
        self._running = True
        
        # 1) Create and connect a new socket in this worker thread.
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect((self.host, self.port))
            print("[MessageUpdaterWorker] Connected to server on separate socket.")
        except ConnectionRefusedError:
            print("[MessageUpdaterWorker] Could not connect to server.")
            self._running = False
        
        # 2) Start polling loop
        while self._running:
            try:
                
                request_data = api.GetMessagesRequest(self.username).pack()
                self._sock.sendall(request_data)
                
                header, recvd = recv_resp_bytes(self._sock)

                if ResponseType(header.header_type) == ResponseType.ERROR:
                    resp = ErrorResponse.unpack(recvd)
                    print(f"[MessageUpdaterWorker] Error: {resp.message}")
                    return
                
                response = api.GetMessagesResponse.unpack(recvd)
                self.messages_received.emit(response.messages)

            except Exception as e:
                print(f"[MessageUpdaterWorker] Error: {e}")
                # On any critical error, you might want to break or handle differently
                break

            # Sleep for the update interval (in seconds)
            time.sleep(self.update_interval)

        # Cleanup
        if self._sock:
            self._sock.close()
            self._sock = None
        print("[MessageUpdaterWorker] Worker thread stopped.")

    def stop(self):
        """
        Signal the worker loop to stop running.
        """
        self._running = False

class Login(QWidget):

    def __init__(self):
        super().__init__()

        self.user_label = QLabel("User: ")
        self.user_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.user_label.setAutoFillBackground(True)

        self.password_label = QLabel("Password: ")
        self.password_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.password_label.setAutoFillBackground(True)
        

        self.user_entry = QLineEdit()
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")

        self.sign_up_button = QPushButton("Sign Up")

        self.entry_layout = QGridLayout()
        self.entry_layout.addWidget(self.user_label, 0, 0)
        self.entry_layout.addWidget(self.user_entry, 0, 1)
        self.entry_layout.addWidget(self.password_label, 1, 0)
        self.entry_layout.addWidget(self.password_entry, 1, 1)
        self.entry_layout.addWidget(self.login_button, 2, 0)
        self.entry_layout.addWidget(self.sign_up_button, 2, 1)

        self.setLayout(self.entry_layout)


class LoggedIn(QWidget):
    def __init__(self):
        super().__init__()
        self.logged_in_layout = QHBoxLayout()
        self.user_label = QLabel("Logged in as: ")
        self.delete_account_button = QPushButton("Delete Account")
        self.sign_out_button = QPushButton("Sign Out")

        self.logged_in_layout.addWidget(self.user_label)
        self.logged_in_layout.addWidget(self.delete_account_button)
        self.logged_in_layout.addWidget(self.sign_out_button)

        self.setLayout(self.logged_in_layout)
    
    def update_user_label(self, username):
        self.user_label.setText(f"Logged in as: {username}")
        
    
class SendMessage(QWidget):
    def __init__(self):
        super().__init__()
        self.frame_layout = QGridLayout()
        self.frame_layout.setSpacing(0)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)

        self.frame_label = QLabel("Send Message")

        self.recipient_label = QLabel("Recipient: ")
        self.recipient_entry = QLineEdit()

        self.message_label = QLabel("Message: ")
        self.message_text = QTextEdit()

        self.send_button = QPushButton("Send")

        self.frame_layout.addWidget(self.frame_label, 0, 0, 1, 2)
        self.frame_layout.addWidget(self.recipient_label, 1, 0)
        self.frame_layout.addWidget(self.recipient_entry, 1, 1)
        self.frame_layout.addWidget(self.message_label, 2, 0)
        self.frame_layout.addWidget(self.message_text, 2, 1)
        self.frame_layout.addWidget(self.send_button, 3, 0, 1, 2)

        self.setLayout(self.frame_layout)


class ListAccount(QWidget):
    def __init__(self):
        super().__init__()
        self.frame_layout = QVBoxLayout()
        self.frame_layout.setSpacing(0)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)

        self.frame_label = QLabel("Search Accounts")
        self.entry_label = QLabel("Search: ")
        self.search_entry = QLineEdit()
        self.search_button = QPushButton("Search")
        self.account_list = QListWidget()

        self.frame_layout.addWidget(self.frame_label)

        self.entry_box = QHBoxLayout()
        self.entry_box.addWidget(self.entry_label)
        self.entry_box.addWidget(self.search_entry)
        self.entry_box.addWidget(self.search_button)

        self.frame_layout.addLayout(self.entry_box)
        self.frame_layout.addWidget(self.account_list)

        self.frame = QFrame()
        self.setLayout(self.frame_layout)

class Central(QWidget):
    def __init__(self, send_message, list_account):
        super().__init__()
        self.send_message = send_message
        self.list_account = list_account

        self.frame_layout = QHBoxLayout()

        self.frame_layout.addWidget(self.send_message)
        self.frame_layout.addWidget(self.list_account)

        
        self.frame = QFrame()
        self.setLayout(self.frame_layout)


class NoLeadingZeroValidator(QIntValidator):
    def validate(self, input_str, pos):
        # Allow empty input (to support deletion)
        if input_str == "":
            return QValidator.Intermediate, input_str, pos
        
        # Prevent leading zeros unless the number is just "0"
        if input_str.startswith("0") and len(input_str) > 1:
            return QValidator.Invalid, input_str, pos  
        
        # Check if input is a valid integer
        try:
            num = int(input_str)
        except ValueError:
            return QValidator.Invalid, input_str, pos
        
        # Ensure it's within the valid range
        if self.bottom() <= num <= self.top():
            return QValidator.Acceptable, input_str, pos
        else:
            return QValidator.Invalid, input_str, pos
    
class ViewMessage(QWidget):
    def __init__(self):
        super().__init__()
        self.frame_layout = QHBoxLayout()
        self.frame_layout.setSpacing(0)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)

        self.frame_label = QLabel("View Messages")

        # TODO add validation to input here
        self.unread_count_label = QLabel("Unread Messages")
        self.num_read_label = QLabel("Number of Messages to Read: ")
        self.num_read_entry = QLineEdit()
        self.num_read_entry.setValidator(NoLeadingZeroValidator(1,100))
        self.read_button = QPushButton("Read Messages")

        self.unread_box = QVBoxLayout()
        self.unread_box.addWidget(self.frame_label)
        self.unread_box.addWidget(self.unread_count_label)
        self.unread_box.addWidget(self.num_read_label)
        self.unread_box.addWidget(self.num_read_entry)
        self.unread_box.addWidget(self.read_button)
        
        self.delete_button = QPushButton("Delete Selected")
        self.unread_box.addWidget(self.delete_button)

        self.message_list = QListWidget()
        self.message_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.message_list.setFont(QFont("Courier", 10))

        self.frame_layout.addLayout(self.unread_box)
        self.frame_layout.addWidget(self.message_list)

        self.setLayout(self.frame_layout)
    
    def update_message_list(self, messages):
        selected_ids = set()
        for item in self.message_list.selectedItems():
            msg = item.data(Qt.UserRole)
            selected_ids.add(msg.id)

        # print(f"Selected IDs pre-refresh: {selected_ids}")

        num_unread = 0

        self.message_list.blockSignals(True)

        self.message_list.clear()
        for message in messages:
            if not message.read:
                num_unread += 1
                continue

            # Convert timestamp to a readable string
            time_str = datetime.fromtimestamp(message.ts).strftime('%Y-%m-%d %H:%M:%S')

            # Create a display string
            display_text = f"[{time_str}] {message.sender}: {message.body}"

            # Create a list item
            item = QListWidgetItem(display_text)

            # Store the entire Message object in user data
            item.setData(Qt.UserRole, message)

            self.message_list.addItem(item)

            # Make sure previously selected items are selected
            if message.id in selected_ids:
                # print(f"Selected ID found: {message.id}")
                item.setSelected(True)

        self.message_list.blockSignals(False)
        self.message_list.repaint()  # Force a refresh only once

        self.unread_count_label.setText(f"Unread Messages: {num_unread}")



def create_main_frame(login, logged_in, central, messages):
    # set up the frame
    main_frame_layout = QVBoxLayout()
    main_frame_layout.setSpacing(0)
    main_frame_layout.setContentsMargins(0, 0, 0, 0)

    # add application frames
    main_frame_layout.addWidget(login)
    main_frame_layout.addWidget(logged_in)
    main_frame_layout.addWidget(central)
    main_frame_layout.addWidget(messages)

    main_frame = QFrame()
    main_frame.setLayout(main_frame_layout)

    return main_frame

class MainFrame(QFrame):
    def __init__(self, login, logged_in, central, view_messages):
        super().__init__()

        self.login = login
        self.logged_in = logged_in
        self.central = central
        self.view_messages = view_messages

        # Set up the frame layout
        main_frame_layout = QVBoxLayout()
        main_frame_layout.setSpacing(0)
        main_frame_layout.setContentsMargins(0, 0, 0, 0)

        # Add application frames
        main_frame_layout.addWidget(login)
        main_frame_layout.addWidget(logged_in)
        main_frame_layout.addWidget(central)
        main_frame_layout.addWidget(view_messages)

        self.setLayout(main_frame_layout)

def create_window(main_frame):
    window = QMainWindow()
    window.setWindowTitle("Message App: Design Exercise")
    window.setCentralWidget(main_frame)
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height())
    return window

def hash_string(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()

def main():
    parser = argparse.ArgumentParser(allow_abbrev=False, description = "GUI for the Message App Design Exercise")

    parser.add_argument("host", type = str, metavar = 'host', help = "The host on which the server is running")

    parser.add_argument("port", type = int, metavar = 'port', help = "The port at which the server is listening")

    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # load GUI
    app = QApplication(argv)

    login = Login()
    logged_in = LoggedIn()

    send_message = SendMessage()
    list_account = ListAccount()
    central = Central(send_message, list_account)
    view_messages = ViewMessage()

    main_frame = MainFrame(login, logged_in, central, view_messages)

    window = create_window(main_frame)

    print(args)

    # hide central frames
    if not args.debug:

        print("Trying to connect to server...")
        logged_in.hide()
        central.hide()
        view_messages.hide()

        user_session = UserSession(args.host, args.port, main_frame, window, False)
    else:
        view_messages.update_message_list(SAMPLE_DATA)
        user_session = UserSession(args.host, args.port, main_frame, window, True)


    # display GUI
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
