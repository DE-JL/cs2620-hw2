# CS 2620: Wire Protocols Design Exercise

> [!NOTE]
> **Authors:** Daniel Li, Rajiv Swamy
> 
> **Date:** 2/12/25

## Usage Instructions
This is app is built in Python.

To run the server and UI Client, do the following:
1. Install the python packages in a virtual environment: 
    - `python3 -m venv venv`
    - `source venv/bin/activate`
    - `pip install -r requirements.txt`
2. Change config settings in `config/config.yaml`
    - If you would like to run the client UI and the server on separate computers, set `network.public_status` to `true`.
      Ensure the client and the server computers are on the same local network. On startup, the server will print its IP address and port.
    - To toggle the wire protocol implementation between JSON and custom, set `protocol_type` to `json` or `custom`.
2. Open a terminal and run the server: `python server.py`
    - If you'd like to run the client UI and the server on separate computers, note the host name and port name in the console output.
3. Run the client: `python client_ui.py [host] [port]` 

## Wire Protocol Design

The assignment specifies that the wire protocol offer two implementations: JSON and a custom protocol. Our wire protocol implementations are located in the `api` directory. Our wire procols essentially manage the serialization and deserialization of the data sent between the client and the server and facilitate management for the user and message entities for the message app (both of these models are implemented in the `entity` directory and are implemented using the Pydantic BaseModel class). Each file in the `api` directory has classes that implement the wire protocol for the corresponding request/response types. The `pack` method of each of these classes encode the data and prepend the protocol header (which delineates by Enum the request/response type and the total size of the data payload). The `unpack` method of each of these classes verify the protocol header and decode the data. 

Our write protocol implements the custom approach and JSON approach within each `unpack` and `pack` method by drawing the protocol selected in the `config/config.yaml` file. The custom protocol is implemented using the struct library (this library works by specifying a format string and packing the data using the format string). The JSON approach is implemented using the standard JSON and the pydantic library model methods for serialization and deserialization. 

## Frontend Approach

The frontend of our app is built with the PyQt library. PyQt was chosen as it fit the class language constraints and had extensive support and documentation. Once the user runs the terminal command to open the UI, they will be presented with a screen to login or create a new account. When the user runs this command, the app will immediately spin up a socket connection with the server through a `UserSession` object. Once authenticated the user will be taken to the main frame of the app, where they can sign out, delete their account, send a message, search existing accounts, and view their messages.
Our app takes an HTTP-esque approach in retrieving and modifying user data. The frontend is responsible for retrieving new state and sending modifications to theserver (i.e., hence our API corresponds to relevant GET, PUT, POST, and DELETE requests for the corresponding user and message entities). Becasue of this design, we designed the frontend to recurrently make GetMessage requests to the server by using a `MessageUpdaterWorker` on a separate thread (this worker uses a different socket connection) and make modifications to the view messages screen accordingly. When the user reads a message or deletes a message, the client sends `read` and `delete` requests to the server respectively. After the server updates the state, the frontend `MessageUpdaterWorker` will update the messages state on the client and emit a signal that tells the UI to update the view messages screen.

## Backend Approach
The backend of our app is implemented in the `server.py` file. The server spins up one socket to handle requests from multiple clients using the selector approach discussed in class. The user and message data persists in memory currently. When the user wants to spin up a client on a public computer (the `public_status` flag is set to `true`), the server will provide descriptive output of the host and port to connect to for the client.

For the backend of this application, there were two main parts: serialization and execution.
The former deals with defining custom serialization methods for all types of data (requests, responses) that are sent over the network.
The latter deals with the logic (data structures, functions) associated with executing each request received from the client.

### Serialization
For each of our request/response and data object classes, we specified a custom serialization format.
To send data over the network, we defined `pack()` and `unpack()` member methods in our classes.
For a particular class `C`, an instance `c` of type `C` can be serialized with `c.pack()`.
Similarly, if the client knows that an array `arr` of bytes represent a serialized `C` object, the client can deserialize the object by calling `C.unpack(arr)`.
Naturally, `pack()` and `unpack()` are inverse operations: they are called prior to sending data and after receiving data.

The fundamental unit of our wire protocol is the _protocol header._ The protocol header looks something like this:

#### Header
```py
class Header:
    header_type: int
    payload_size: int
```

The `header_type` field specifies what kind of request/response the server/client received.
The `payload_size` field specifies how large (in bytes) the incoming data stream is.
The serialization format looks like `<HEADER_TYPE : 4 byte int> <PAYLOAD_SIZE : 4 byte int>`.
This imposes a restriction on the amount of data we can send over the network at a time: $2^{32}$ bytes, or 4 GB.
However, we make the assumption that neither the client nor the server will send/receive 4 GB of information in any one `send()` or `recv()` call.

For each of the request/response and classes, the custom `pack()` method will always preprend the protocol header in the very front.
Conversely, for `unpack()`, the protocol header is always assumed to be there, and must be extracted prior to unpacking the actual payload.

#### Message Class
A more complex example of this is our message class:

```py
class Message:
    sender: str
    receiver: str
    body: str
    id: uuid.UUID
    ts: float
    read: bool
```

whose serialization format looks like:

```
<HEADER>...
<SENDER_LEN : 4-byte int>...
<RECEIVER_LEN : 4-byte int>...
<BODY_LEN : 4-byte int>...
<SENDER_BYTES : char[]>...
<RECEIVER_BYTES : char[]>...
<BODY_BYTES : char[]>...
<MESSAGE_ID : 16-byte array>...
<TIMESTAMP : 8-byte double>
```

The actual construction of the resulting bytes was handled by Python's [struct](https://docs.python.org/3/library/struct.html) package.
This package allowed us to specify complex formats and serialize variable-lengthed data (strings).

#### JSON
For JSON, we defined all of our classes to inherit from Python's pydantic [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) class.
`BaseModel` objects have a `model_dump_json()` member function that converts the object into a valid JSON string.
Our `Message` JSON serialization branch looks as follows:

```py
class Message(BaseModel):
    ...

    def pack()
        ... [JSON branch of message.pack()]
        # Encode the data
        json_str = self.model_dump_json()
        data = json_str.encode("utf-8")
        
        # Prepend the protocol header
        header = Header(header_type=DataType.MESSAGE.value,
                        payload_size=len(data))
        return header.pack() + data
```

#### Custom Serialization vs. JSON
We've attached the server traffic volume (both sent and received) in our debug logs to check the size of the messages under different serialization protocols.
The following two blocks are the server's final debug statements when running the _integration tests_ (which submit a bunch of queries)
with the custom serialization protocol and JSON, respectively.

##### Custom
```
-------------------------------- SERVER STATE (CUSTOM) --------------------------------
USERS: {'user1': User(username='user1', password='password', message_ids=set())}
MESSAGES: {}
TOTAL TRAFFIC (INBOUND): 856 bytes
TOTAL TRAFFIC (OUTBOUND): 1077 bytes
------------------------------------------------------------------------------
```

##### JSON
```
-------------------------------- SERVER STATE (JSON) ----------------------------------
USERS: {'user1': User(username='user1', password='password', message_ids=set())}
MESSAGES: {}
TOTAL TRAFFIC (INBOUND): 1768 bytes
TOTAL TRAFFIC (OUTBOUND): 1674 bytes
---------------------------------------------------------------------------------------
```

Evidently, JSON almost _doubles_ the number of bytes sent over the network.
Furthermore, this is only over two clients and a very small number (~20) of queries.
As the application scales, we will want to have more compact serialization protocols if the network becomes a bottleneck.

### Execution
Since we are not persisting chat information to disk, all information regarding users and messages is stored in memory by the server.

```py
class Server:
    def __init__(self):
        self.users: dict[str, User] = {}
        self.messages: dict[uuid.UUID, Message] = {}
```

Users are identified by their unique alphanumeric username.
Messages are identified by a 16-byte UUID that is assigned on the _client_ side.
These two dictionaries comprise of all the data stored by our server at any given time.

#### Request Handling
Upon receiving a request, the server first determines the request type by examining the protocol header.
It will then deserialize the bytes using the `unpack()` method associated with the request type.

The server has a request handler for each particular type of request.
It will pass the request to the appropriate handler.
The handler will execute the request, modifying the server state if necessary.

The function signature of each request handler looks something like:
```py
def handler(ctx: types.SimpleNamespace, request: Request):
    ... do stuff
    resp = Response()
    ctx.outbound += resp.pack()
```

The context is the namespace associated with a particular connection that was initialized in the `accept_wrapper()`.
This was given in the starter code. Once a response has been written to the `outbound` field of a context, the server selector will eventually
send the response back to the client.

The implementation details of each particular request handler are not complicated, so we will omit the details here.

#### Sending Messages
Our implementation does not allow a user to view the history of the messages they have sent.
This was a decision that was made because the assignment specifications and discussions with the course staff have made it clear
that only the user who _receives_ a message can delete it.
To simplify our implementation, we have made it so that once a message is sent, the sender no longer has any association with the message.

#### Deleting a User
As for the project specifications, we must specify what happens to unread messages on a **delete user request.**
Our implementation will delete all the user's received messages regardless of whether they are unread or not.

## Testing
Both unit tests and integration tests are provided.

To run the tests:
1. Open a terminal and activate the virtual  environment: `source venv/bin/activate`.
2. Run the tests: `python -m pytest tests`.

### Serialization Tests
The serialization methods for all classes were tested by verifying that `pack()` and `unpack()` were inverse operations
as well as some other equality checks.
This was done in `tests/test_wire_protocol.py`.

### Unit Tests
For unit testing, a server instance was started but set so that it would not listen for client connections.
Instead, the requests were _mocked_ by calling the server's request handlers manually.
The test details can be found in `tests/test_server_unit.py`.

### Integration Tests
Integration tests were done in `tests/test_integration.py`.
These tests were essentially the same as the unit tests except a client-server connection was established, and 
requests were sent over to the server over the network instead of calling the request handlers manually.
