import socket
import threading
import ssl
from handler import handle_http1
from sessions import get_session_id_from_request,cookie_response,get_session,create_session

# Server Configuration
HOST = '127.0.0.1'
PORT = 9090


def start_server():
    try:
        # Create a socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"Server started on {HOST}:{PORT}")

      

        while True:
            try:
                
                client_socket, client_address = server.accept()
                print(f"New connection from {client_address}")    
                # Handle each client in a new thread
                threading.Thread(target=handle_http1, args=(client_socket, client_address), daemon=True).start()

            except Exception as e:
                print(f"Error accepting a connection: {e}")

    except Exception as e:
        print(f"Server failed to start: {e}")
    finally:
        print("Shutting down the server")
        server.close()

if __name__ == "__main__":
    start_server()
