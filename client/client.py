import socket

HOST = '127.0.0.1'
PORT = 8080


def run_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        print("Connected to server.")

        while True:
            # Take user input
            message = input("Enter a message to send to the server (type 'exit' to quit): ")
            if message.lower() == 'exit':
                print("Closing connection...")
                break

            # Send message to the server
            client.sendall(message.encode('utf-8'))

            # Receive and print the server's response
            response = client.recv(1024)
            print(f"Server Response: {response.decode('utf-8')}")


if __name__ == "__main__":
    run_client()
