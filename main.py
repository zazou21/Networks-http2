from Server.server import start_server
from Server.monitor import monitor_server
import threading

if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    threading.Thread(target=monitor_server).start()
