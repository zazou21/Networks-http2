import threading
import time

# Global variable to keep track of active connections
active_connections = 0

# Lock to ensure thread safety when updating the active connection count
connections_lock = threading.Lock()


# Function to update the active connections count safely
def update_connections(change):
    global active_connections
    with connections_lock:  # Ensure thread safety
        active_connections += change


# Monitor function that prints the current number of active connections
def monitor_server():
    while True:
        with connections_lock:  # Ensure thread safety when accessing the global variable
            print(f"Active connections: {active_connections}")
        time.sleep(5)  # Print every 5 seconds
