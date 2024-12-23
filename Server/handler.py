# HTTP/2 connection preface


import ssl
from sessions import Session, generate_session_id, get_session_id_from_request,cookie_response,get_session,create_session,sessions
from http_module import *

HTTP2_PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"




# def handle_http1(client_socket, client_address):
#     try:
#         print(f"Handling client {client_address} using http1")

#         client_socket.settimeout(10)  # Optional timeout
#         request_data = client_socket.recv(1024).decode('utf-8', errors='ignore')  
#     except client_socket.timeout:
#         print(f"Client {client_address} timed out")
#     except Exception as e:
#         print(f"Error handling client {client_address}: {e}")
  
#     print(f"Handling HTTP/1.1 request from {client_address} \n")

#     print(f"{request_data} \n")

  
    # Process other HTTP/1.1 requests (e.g., GET and POST)
def handle_http1(client_socket, client_address):
    try:
        print(f"Handling client {client_address} using HTTP/1")

        client_socket.settimeout(10)
        request_data = client_socket.recv(1024).decode('utf-8', errors='ignore')

        http_request = HttpRequest(request_data)
        session=None

        session_id = get_session_id_from_request(request_data)

        if session_id in sessions:
            print(f"Valid session found for {client_address}: {session_id}")
            session = sessions[session_id]
            print(f"The username saved in session data is {session.username}")

        else:
            print(f"No valid session for {client_address}, creating a new one.")
            session = create_session()
            cookie_response(client_socket, session.session_id)  # Send session cookie to client


        if http_request.method == "GET":
            handle_GET(client_socket, http_request)
        elif http_request.method == "POST":

            handle_POST(client_socket, session, http_request)

    except ssl.SSLError as e:
        print(f"SSL error with client {client_address}: {e}")
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()


def handle_GET(client_socket, GET_request):
    if GET_request.path == "/":
        with open("files/index.html", "r") as file:
            html_content = file.read()
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(html_content)}\r\n"
            "\r\n"
            f"{html_content}"
        )
        client_socket.sendall(response.encode('utf-8'))
    else:
        try:
            with open(f"files/{GET_request.path}.html", "r") as file:
                html_content = file.read()
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    f"Content-Length: {len(html_content)}\r\n"
                    "\r\n"
                    f"{html_content}"
                )
                client_socket.sendall(response.encode('utf-8'))
        except FileNotFoundError:
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                "Content-Length: 29\r\n"
                "\r\n"
                "<h1>404 Not Found</h1>"
            )
            client_socket.sendall(response.encode('utf-8'))


def handle_POST(client_socket, session, http_request):
    form_data = http_request.body.split("&")
    form_data = dict(item.split("=") for item in form_data)
        
        # Extract the "name" and "message" fields
    name = form_data.get("name", "Unknown")
    message = form_data.get("message", "No message")

    session.username=name

    response_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Submission Response</title>
    </head>
    <body>
        <h1>Form Submitted!</h1>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Message:</strong> {message}</p>
        <p><a href="/">Go back</a></p>
    </body>
    </html>
    """
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        f"Set-Cookie: session_id={session.session_id}; HttpOnly; Secure; Max-Age=3600\r\n"
        f"Content-Length: {len(response_content)}\r\n"
        "\r\n"
        f"{response_content}"
    )
    client_socket.sendall(response.encode('utf-8'))


def handle_http2(client_socket, client_address):
    """Handles HTTP/2 requests."""
    try:
        print(f"Handling HTTP/2 request from {client_address}")
        client_socket.settimeout(10)  # Optional timeout

        # Step 1: Validate the HTTP/2 connection preface
        preface = client_socket.recv(24)
        if preface != HTTP2_PREFACE:
            print(f"Invalid HTTP/2 preface from {client_address}")
            client_socket.close()
            return

        print(f"HTTP/2 preface received from {client_address}")

        # Step 2: Send a SETTINGS frame
        settings_frame = b'\x00\x00\x06'  # Length: 6
        settings_frame += b'\x04'         # Type: SETTINGS
        settings_frame += b'\x00'         # Flags
        settings_frame += b'\x00\x00\x00\x00'  # Stream ID: 0
        settings_frame += b'\x00\x01\x00\x00\x00\x64'  # Example: max concurrent streams = 100
        client_socket.sendall(settings_frame)
        print(f"SETTINGS frame sent to {client_address}")

        # Step 3: Respond with HEADERS and DATA frames
        # Headers (HPACK-encoded, simplified for now)
        encoded_headers = b'\x88\x03\x33\x30\x32' 
        headers_frame = b'\x00\x00\x05'  # Length: 5
        headers_frame += b'\x01'         # Type: HEADERS
        headers_frame += b'\x05'         # Flags (END_HEADERS | END_STREAM)
        headers_frame += b'\x00\x00\x00\x01'  # Stream ID: 1
        headers_frame += encoded_headers

        data_frame = b'\x00\x00\x0d'  # Length: 13
        data_frame += b'\x00'         # Type: DATA
        data_frame += b'\x01'         # Flags (END_STREAM)
        data_frame += b'\x00\x00\x00\x01'  # Stream ID: 1
        data_frame += b'Hello, HTTP/2!'

        client_socket.sendall(headers_frame + data_frame)
        print(f"Response sent to {client_address}")

    except ssl.SSLError as e:
        print(f"SSL error with client {client_address}: {e}")
    except client_socket.timeout:
        print(f"Client {client_address} timed out")
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        try:
            client_socket.close()
        except Exception as e:
            print(f"Error closing socket for {client_address}: {e}")









def redirect_to_login(client_socket):
    """Redirect the client to the login page"""
    with open("files/login.html", "r") as file:
            html_content = file.read()
            response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(html_content)}\r\n"
            "\r\n"
            f"{html_content}"
        )
    client_socket.sendall(response.encode('utf-8'))
   


def handle_login(client_socket, request_data):
    print("Handling login...")  # Debugging line to ensure it's being called

    body = request_data.split("\r\n\r\n")[1]
    form_data = dict(item.split("=") for item in body.split("&"))
    username = form_data.get("username", "Unknown")

    print(f"Username submitted: {username}")  # Debugging line to see the username submitted

    session_id = generate_session_id()
    session = Session(session_id, username)

    # Store the session in the sessions dictionary
    sessions[session_id] = session

    # Respond with a 302 redirect to the home page
    response = (
        "HTTP/1.1 302 Found\r\n"
        "Location: /index.html\r\n"  # Redirect to the home page
        f"Set-Cookie: session_id={session.session_id}; HttpOnly; Secure; Max-Age=3600\r\n"  # Session cookie
        "Content-Length: 0\r\n"  # No content in this response
        "\r\n"
    )

    client_socket.sendall(response.encode('utf-8'))
