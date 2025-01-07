import socket
import threading
import ssl
from handler import handle_http2

threads = []

# Server Configuration
HOST = "127.0.0.1"
PORT = 8085

CERT_FILE = "D:/Senior1/Networks/Project/Server/server.crt"
KEY_FILE = "D:/Senior1/Networks/Project/Server/server.key"


def start_server():
    try:
        # Create a socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"Server started on {HOST}:{PORT}")

        try:
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

            # Disable hostname checking and certificate validation for self-signed certificates
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE  # Skip certificate validation

            # Load the server's certificate and private key
            context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

            # Set ALPN protocols to support HTTP/2 and HTTP/1.1
            context.set_alpn_protocols(["h2", "http/1.1"])

        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            return

        while True:
            try:
                # Accept new connections
                client_socket, client_address = server.accept()
                print(f"New connection from {client_address}")

                # Wrap the socket with SSL context to handle ALPN negotiation
                secure_socket = context.wrap_socket(client_socket, server_side=True)

                # Check the selected protocol after ALPN negotiation
                selected_protocol = secure_socket.selected_alpn_protocol()
                if selected_protocol == "h2":
                    print(f"Client {client_address} upgraded to HTTP/2")
                else:
                    print(f"Client {client_address} is using HTTP/1.1")

                # Handle each client in a new thread
                thread = threading.Thread(
                    target=handle_http2,
                    args=(secure_socket, client_address),
                    daemon=True,
                )
                threads.append(thread)
                thread.start()

            except Exception as e:
                print(f"Error accepting a connection: {e}")

    except Exception as e:
        print(f"Server failed to start: {e}")
    finally:
        print("Shutting down the server")
        server.close()


if __name__ == "__main__":
    start_server()
