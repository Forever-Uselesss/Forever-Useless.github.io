import http.server
import socketserver
import threading
import time

# Define the port you want to use
PORT = 8080

## timeout variable change here to set the idle timeout
timeout = 60  
# Idle timeout in seconds

# Define the handler to serve files
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global last_activity_time
        last_activity_time = time.time()  # Update the last activity time on every request
        super().do_GET()

# Create a server class with idle timeout monitoring
class ServerWithTimeout:
    def __init__(self, host='', port=PORT, idle_timeout=60):
        self.host = host
        self.port = port
        self.idle_timeout = idle_timeout
        self.server = socketserver.TCPServer((host, port), CustomHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def start(self):
        global last_activity_time
        last_activity_time = time.time()  # Initialize the last activity time
        print(f"Serving at http://{self.host or 'localhost'}:{self.port}")
        self.server_thread.start()
        self._monitor_timeout()

    def _monitor_timeout(self):
        while True:
            time.sleep(1)
            if time.time() - last_activity_time > self.idle_timeout:
                print("No activity detected. Shutting down the server.")
                self.stop()
                break

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        print("Server has been stopped.")

if __name__ == "__main__":
    # Set idle timeout in timeout variable
    server = ServerWithTimeout(idle_timeout = timeout)
    try:
        server.start()
    except KeyboardInterrupt:   
        print("\nServer interrupted by user.")
        server.stop()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        server.stop()
    except SystemExit:
        print("\nServer stopped.")
        server.stop()   