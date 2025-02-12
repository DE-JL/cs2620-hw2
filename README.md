# COS 2620: Wire Protocol Design Exercise
## Authors: Daniel Li and Rajiv Swamy

## Usage Instructions for the Message App Design Exercise
This is app is built in Python.

To run the server and UI Client, do the following:
1. Install the python packages in a virtual environment: 
    - `python3 -m venv venv`
    - `source venv/bin/activate`
    - `pip install -r requirements.txt`
2. Change config settings in `config/config.yaml`
    - If you'd like to run the client UI and the server on separate computers, set `network.public_status` to `true`. Ensure the client and the server computers are on the same network.
    - To toggle the wire protocol implementation between JSON and custom, set `protocol_type` to `json` or `custom`.
2. Open a terminal and run the server: `python server.py`
    - If you'd like to run the client UI and the server on separate computers, note the host name and port name in the console output.
3. Run the client: `python client_ui.py [host] [port]` 

## Wire Protocol Design

The assignment specifies that the wire protocol offer two implementations: JSON and a custom protocol. Our wire protocol implementations are located in the `api` directory. Our wire procols essentially manage the serialization and deserialization of the data sent between the client and the server and facilitate management for the user and message entities for the message app (both of these models are implemented in the `entity` directory and are implemented using the Pydantic BaseModel class). Each file in the `api` directory has classes that implement the wire protocol for the corresponding request/response types. The `pack` method of each of these classes encode the data and prepend the protocol header (which delineates by Enum the request/response type and the total size of the data payload). The `unpack` method of each of these classes verify the protocol header and decode the data. 

Our write protocol implements the custom approach and JSON approach within each `unpack` and `pack` method by drawing the protocol selected in the `config/config.yaml` file. The custom protocol is implemented using the struct library (this library works by specifying a format string and packing the data using the format string). The JSON approach is implemented using the standard JSON and the pydantic library model methods for serialization and deserialization. 

## Frontend Approach

The frontend of our app is built with the PyQT library. PyQT was chosen as it fit the class language constraints and had extensive support and documentation. Once the user runs the terminal command to open the UI, they will be presented with a screen to login or create a new account. When the user runs this command, the app will immediately spin up a socket connection with the server through a `UserSession` object. Once authenticated the user will be taken to the main frame of the app, where they can sign out, delete their account, send a message, search existing accounts, and view their messages.
Our app takes an HTTP-esque approach in retrieving and modifying user data. The frontend is responsible for retrieving new state and sending modifications to theserver (i.e., hence our API corresponds to relevant GET, PUT, POST, and DELETE requests for the corresponding user and message entities). Becasue of this design, we designed the frontend to recurrently make GetMessage requests to the server by using a `MessageUpdaterWorker` on a separate thread (this worker uses a different socket connection) and make modifications to the view messages screen accordingly. When the user reads a message or deletes a message, the client sends `read` and `delete` requests to the server respectively. After the server updates the state, the frontend `MessageUpdaterWorker` will update the messages state on the client and emit a signal that tells the UI to update the view messages screen.

## Backend Approach

The backend of our app is implemented in the `server.py` file and spins up one socket to handle requests from multiple clients using the selector approach discussed in class. The user and message data persists in memory currently. When the user wants to spin up a client on a public computer (the `public_status` flag is set to `true`), the server will provide descriptive output of the host and port to connect to for the client.

## Testing

We have developed a set of unit and integration tests for the write protocol, server, and client logic.

### Instructions

To run the tests, do the following:
1. Open a terminal and activate the virtual  environment: `source venv/bin/activate`
2. Run the tests: `python -m pytest tests`

### Server Unit Tests

### Wire Protocol Unit Tests

### Integration Tests
