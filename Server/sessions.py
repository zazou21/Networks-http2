import uuid
from http_module import create_response_frame


class Session:
    def __init__(self, session_id, username="Guest"):
        self.session_id = session_id
        self.username = username

    def to_dict(self):
        return {"user_name": self.username}


# Centralized session store
sessions = {}


def generate_session_id():
    return str(uuid.uuid4())


def create_session(username="Guest"):
    session_id = generate_session_id()
    session = Session(session_id, username)
    sessions[session_id] = session
    return session


def get_session(session_id):
    return sessions.get(session_id)


def cookie_response(client_socket, session_id, current_stream_id, dynamic_table):

    # Read the index.html file
    with open("files/index.html", "r") as file:
        html_content = file.read()

    response_headers = [
        (":status", "200"),
        ("content-type", "text/html"),
        ("content-length", str(len(html_content))),
        ("set-cookie", f"session_id={session_id}"),
    ]

    response = create_response_frame(
        response_headers, html_content, current_stream_id, dynamic_table
    )
    client_socket.sendall(response)


def get_session_id_from_request(request_data):
    cookies = {}
    for line in request_data.split("\r\n"):
        if line.lower().startswith("cookie:"):
            cookie_header = line.split(":", 1)[1].strip()
            for cookie in cookie_header.split(";"):
                key, value = cookie.strip().split("=", 1)
                cookies[key] = value
    return cookies.get("session_id")
