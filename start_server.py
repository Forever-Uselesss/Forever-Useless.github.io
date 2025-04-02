import http.server
import socketserver
import threading
import time

# Define the port you want to use
PORT = 8080

## timeout variable change here to set the idle timeout
timeout = -1 
# Idle timeout in seconds (-1 to disable)

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
        self._shutdown_flag = False

    def start(self):
        global last_activity_time
        last_activity_time = time.time()  # Initialize the last activity time
        print(f"Serving at http://{self.host or 'localhost'}:{self.port}")
        self.server_thread.start()
        if self.idle_timeout != -1:
            self._monitor_timeout()
        else:
            print("Idle timeout is disabled.")

    def _monitor_timeout(self):
        while not self._shutdown_flag:
            # Check for inactivity
            time.sleep(1)
            if time.time() - last_activity_time > self.idle_timeout:
                print("No activity detected. Shutting down the server.")
                self.stop()
                break

    def stop(self):
        self._shutdown_flag = True
        self.server.shutdown()
        self.server.server_close()
        print("Server has been stopped.")

if __name__ == "__main__":
    # Set idle timeout in timeout variable
    server = ServerWithTimeout(idle_timeout=timeout)
    try:
        server.start()
        # If timeout is disabled, keep the main thread alive
        if timeout == -1:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:   
        print("\nServer interrupted by user.")
        server.stop()
        exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        server.stop()
        exit(1)
# This script creates a simple HTTP server that serves files from the current directory.