import ssl
from sessions import (
    Session,
    generate_session_id,
    get_session_id_from_request,
    cookie_response,
    get_session,
    create_session,
    sessions,
)
from http_module import *
from Frames import *
from HPACK import *
from HPACK import encode_header, encode_integer, encode_string
import os
import json

import json


def handle_head(client_socket, head_request, current_stream_id, dynamic_table):
    if head_request.path == "/" or head_request.path == "/index.html":

        with open("files/index.html", "r") as file:
            html_content = file.read()

        headers = [
            (":status", "200"),
            ("content-type", "text/html"),
            ("content-length", f"{len(html_content)}"),
        ]

        print(headers)

        encoded_headers = []
        for name, value in headers:
            encoded_headers.extend(encode_header(name, value, dynamic_table))

        encoded_headers_bytes = bytes(encoded_headers)

        headers_frame = (
            get_response_size(encoded_headers_bytes)  # Length of the encoded headers
            + b"\x01"  # Type: HEADERS
            + b"\x04"  # Flags: END_HEADERS
            + current_stream_id.to_bytes(4, byteorder="big")  # request stream ID
            + encoded_headers_bytes
        )
        client_socket.sendall(headers_frame)

    else:

        try:
            with open(f"files/{head_request.path}", "r") as file:
                html_content = file.read()

            headers = [
                (":status", "200"),
                ("content-type", "text/html"),
                ("content-length", f"{len(html_content)}"),
            ]

            encoded_headers = []
            for name, value in headers:
                encoded_headers.extend(encode_header(name, value, dynamic_table))

            encoded_headers_bytes = bytes(encoded_headers)

            headers_frame = (
                get_response_size(
                    encoded_headers_bytes
                )  # Length of the encoded headers
                + b"\x01"  # Type: HEADERS
                + b"\x04"  # Flags: END_HEADERS
                + current_stream_id.to_bytes(4, byteorder="big")  # request stream ID
                + encoded_headers_bytes
            )
            client_socket.sendall(headers_frame)

        except FileNotFoundError:

            headers = [
                (":status", "404"),
            ]

            encoded_headers = []
            for header in headers:
                encoded_headers.append(encode_header(header))

            encoded_headers_bytes = bytes(encoded_headers)

            headers_frame = (
                get_response_size(encoded_headers_bytes)
                + b"\x01"
                + b"\x04"
                + current_stream_id.to_bytes(4, byteorder="big")  # request stream ID
                + encoded_headers_bytes
            )
            client_socket.sendall(headers_frame)


def handle_put(client_socket, put_request, current_stream_id, dynamic_table):

    body_data = put_request.body

    try:
        # Decode and parse the body data
        body = body_data.decode("utf-8")
        json_data = json.loads(body)

        name_to_update = json_data.get("name")
        new_name = json_data.get("new_name")

        if not name_to_update or not new_name:
            response_content = json.dumps(
                {"error": "'name' or 'new_name' field not found in the request body."}
            )
            status_code = "400"
        else:
            print(f"Attempting to update name: {name_to_update} to {new_name}")
            file_path = "files/names.txt"

            with open(file_path, "r") as file:
                names = file.readlines()

            if name_to_update not in [n.strip() for n in names]:
                response_content = json.dumps(
                    {"error": f"Name '{name_to_update}' not found in the file."}
                )
                status_code = "404"
            else:

                update_name(file_path, name_to_update, new_name)
                response_content = json.dumps(
                    {
                        "message": f"Name '{name_to_update}' updated to '{new_name}' successfully."
                    }
                )
                status_code = "200"

    except json.JSONDecodeError:
        response_content = json.dumps({"error": "Invalid JSON format in request body."})
        status_code = "400"
    except Exception as e:
        response_content = json.dumps({"error": f"Unexpected error: {str(e)}"})
        status_code = "500"

    # Prepare headers for the response
    headers = [
        (":status", status_code),
        ("content-type", "application/json"),
        ("content-length", str(len(response_content))),
    ]

    response = create_response_frame(
        headers, response_content, current_stream_id, dynamic_table
    )

    client_socket.sendall(response)


def update_name(file_path, name_to_update, new_name):
    """Updates a name in the file (PUT equivalent)."""
    try:
        # Read all names into a list
        with open(file_path, "r") as file:
            names = file.readlines()

        # Search for the name to update
        names = [new_name if n.strip() == name_to_update else n for n in names]

        # Write the updated names back to the file
        with open(file_path, "w") as file:
            file.writelines(names)

        print(f"Name '{name_to_update}' updated to '{new_name}'.")
    except FileNotFoundError:
        print("File not found. Make sure the file exists.")


def delete_name(file_path, name):
    """Deletes a name from the file (DELETE equivalent)."""
    try:
        # Read all names into a list
        with open(file_path, "r") as file:
            names = file.readlines()

        # Remove the name if it exists
        names = [n for n in names if n.strip() != name]

        # Write the updated names back to the file
        with open(file_path, "w") as file:
            file.writelines(names)

        print(f"Name '{name}' deleted.")
    except FileNotFoundError:
        print("File not found. Make sure the file exists.")


HTTP2_PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"


def handle_delete(client_socket, delete_request, current_stream_id, dynamic_table):

    body_data = delete_request.body

    try:
        body = body_data.decode("utf-8")
        json_data = json.loads(body)

        name_to_delete = json_data.get("name")

        if name_to_delete:
            print(f"Deleting name: {name_to_delete}")
            file_path = "files/names.txt"
            delete_name(file_path, name_to_delete)

            response_content = f"Name '{name_to_delete}' deleted successfully."

        else:

            response_content = "Error: 'name' field not found in the request body."

    except json.JSONDecodeError:
        response_content = "Error: Invalid JSON format in request body."
    except Exception as e:
        response_content = f"Error: {str(e)}"

    # Prepare headers and response
    headers = [
        (":status", "200" if name_to_delete else "400"),
        ("content-type", "text/plain"),
        ("content-length", str(len(response_content))),
    ]

    response = create_response_frame(
        headers, response_content, current_stream_id, dynamic_table
    )
    client_socket.sendall(response)


def handle_GET(client_socket, GET_request, current_stream_id, dynamic_table):
    if GET_request.path == "/" or GET_request.path == "/index.html":

        with open("files/index.html", "r") as file:
            html_content = file.read()

        push_files = []
        if ".html" in GET_request.path or GET_request.path == "/":
            css_file = f"files{GET_request.path}.css"
            js_file = f"files{GET_request.path}script.js"

            if os.path.exists(css_file):
                push_files.append(f"{GET_request.path}.css")

            if os.path.exists(js_file):
                push_files.append(f"{GET_request.path}.js")

        for push_file in push_files:
            push_headers = [
                (":method", "GET"),
                (":scheme", "https"),
                (":authority", "127.0.0.1:8085"),
                (":path", push_file),
            ]
            encoded_push_headers = []
            for name, value in push_headers:
                encoded_push_headers.extend(encode_header(name, value, dynamic_table))

            encoded_push_headers_bytes = bytes(encoded_push_headers)

            push_frame = (
                get_response_size(
                    encoded_push_headers_bytes
                )  # Length of the encoded headers
                + b"\x05"
                + current_stream_id.to_bytes(4, byteorder="big")  # Request stream ID
                + (current_stream_id + 2).to_bytes(
                    4, byteorder="big"
                )  # Push stream ID (new stream ID)
                + encoded_push_headers_bytes
            )
            client_socket.sendall(push_frame)  # Send the push promise frame

        headers = [
            (":status", "200"),
            ("content-type", "text/html"),
            ("content-length", f"{len(html_content)}"),
        ]

        print(headers)

        print(f"content length is {len(html_content)}")

        response = create_response_frame(
            headers, html_content, current_stream_id, dynamic_table
        )
        client_socket.sendall(response)

    else:

        try:
            with open(f"files/{GET_request.path}", "r") as file:
                html_content = file.read()

            headers = [
                (":status", "200"),
                ("content-type", "text/html"),
                ("content-length", f"{len(html_content)}"),
            ]

            print(f"content length is {len(html_content)}")
            response = create_response_frame(
                headers, html_content, current_stream_id, dynamic_table
            )
            client_socket.sendall(response)

        except:

            headers = [
                (":status", "404"),
            ]

            data_payload = "<h1>404 Not Found</h1>".encode("utf-8")

            response = create_response_frame(
                headers, data_payload, current_stream_id, dynamic_table
            )

            client_socket.sendall(response)


def handle_POST(client_socket, request, current_stream_id, dynamic_table, session):

    form_data = request.body.decode("utf-8").split("&")
    form_data = dict(item.split("=") for item in form_data)

    # Extract the "name" and "message" fields
    name = form_data.get("name", "Unknown")
    message = form_data.get("message", "No message")

    session.username = name

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
    headers = [
        (":status", "200"),
        ("content-type", "text/html"),
        ("content-length", f"{len(response_content)}"),
    ]

    response = create_response_frame(
        headers, response_content, current_stream_id, dynamic_table
    )
    client_socket.sendall(response)


def handle_http2(client_socket, client_address):
    """Handles HTTP/2 requests."""
    try:
        dynamic_table = DynamicTable()

        current_stream_id = 1  # Start with stream ID 1 as per HTTP/2 spec

        print(f"Handling HTTP/2 connection from {client_address}")

        print("Sent SETTINGS frame")

        session_id = None

        while 1:
            print(f"Handling HTTP/2 request from {client_address}")

            # client_socket.settimeout(0.5)

            raw_data = client_socket.recv(4096)
            # print(f"Received raw data: {raw_data}")

            if not raw_data:
                print(f"No data received from {client_address}, closing connection.")

                goaway_frame = (
                    b"\x00\x00\x08"
                    + b"\x07"
                    + b"\x00"
                    + b"\x00\x00\x00\x00"
                    + b"\x00\x00\x00\x00"
                    + b"\x00"
                )
                client_socket.sendall(goaway_frame)  # Send GOAWAY frame
                print("Sent GOAWAY frame")
                break

            frames = parse_all_http2_frames(raw_data)

            request = None
            for frame in frames:
                current_stream_id = frame.stream_id
                print(f"Frame received: {frame}")
                if frame.frame_type == "HEADERS":

                    headers = frame.payload
                    print(f"Headers payload {headers}")

                    headers = decode_hpack(headers[5:])
                    filtered_headers = [
                        (name, value) for name, value in headers if name and value
                    ]

                    print(filtered_headers)

                    # headers = payload[9:]
                    cookie_header = next(
                        (value for key, value in headers if key.lower() == "cookie"),
                        None,
                    )

                    # Extract the session_id from the cookie header

                    if cookie_header:
                        cookies = cookie_header.split(
                            ";"
                        )  # Split multiple cookies if present
                        for cookie in cookies:
                            name, _, value = cookie.strip().partition("=")
                            if name == "session_id":
                                session_id = value

                    if session_id and session_id in sessions:
                        print(
                            f"valid session id found for {client_address}: {session_id}"
                        )
                        session = sessions[session_id]
                        print(
                            f"The username saved in this session is {session.username}"
                        )

                    else:
                        print(
                            f"No valid session found for {client_address}, creating a new one"
                        )
                        session = create_session()

                        cookie_response(
                            client_socket,
                            session.session_id,
                            current_stream_id,
                            dynamic_table,
                        )

                    method = None
                    path = None
                    body = None
                    for name, value in headers:
                        if name == ":method":
                            method = value
                        elif name == ":path":
                            path = value
                        elif name == "content-length":
                            # Body length could be determined by content-length, but for simplicity, we skip it here
                            pass
                    if method == "GET":
                        request = HttpRequest2(
                            method, path if path is not None else "/"
                        )
                    if method == "HEAD":
                        request = HttpRequest2(
                            method, path if path is not None else "/"
                        )

                elif frame.frame_type == "DATA":
                    # Extract the body from DATA frame
                    body_data = frame.payload  # Assuming the payload contains the body
                    # print(f"Received body data: {body_data}")
                    request = None
                    if path and method:
                        request = HttpRequest2(method, path)
                    #    print(f"request method {request.method} and request path {request.path}")
                    # Append the body data to the existing body
                    if request:
                        request.body = body_data
                        print(f"Updated body: {request.body}")

                        print(
                            f"request method {request.method} , request path {request.path} and request body {request.body}"
                        )

                if request and request.method == "HEAD":

                    handle_head(
                        client_socket, request, current_stream_id, dynamic_table
                    )

                if request and request.method == "GET":
                    handle_GET(client_socket, request, current_stream_id, dynamic_table)

                if request and request.method == "POST" and request.body is not None:
                    handle_POST(
                        client_socket,
                        request,
                        current_stream_id,
                        dynamic_table,
                        session,
                    )
                    print(f"post response sent to {client_address}")

                if request and request.method == "DELETE" and request.body is not None:
                    handle_delete(
                        client_socket, request, current_stream_id, dynamic_table
                    )
                    print(f"delete response sent to {client_address}")

                if request and request.method == "PUT" and request.body is not None:
                    handle_put(client_socket, request, current_stream_id, dynamic_table)
                    print(f"put response sent to {client_address}")

    except ssl.SSLError as e:
        print(f"SSL error with client {client_address}: {e}")
    except client_socket.timeout:
        print(f"Client {client_address} timed out")
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
