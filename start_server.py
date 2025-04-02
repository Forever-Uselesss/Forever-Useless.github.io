import http.server
import socketserver
import threading
import time
import os

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
        
        # Check if the requested path exists
        if not self.path_exists():
            self.send_404()
            return
            
        super().do_GET()
    
    def path_exists(self):
        # Translate the path to a filesystem path
        path = self.translate_path(self.path)
        
        # For root path, check if index.html exists
        if self.path == '/':
            return os.path.exists(os.path.join(path, 'index.html')) or os.path.exists(os.path.join(path, 'index.htm'))
        
        # For all other paths, check if the file exists
        return os.path.exists(path)
    
    def send_404(self):
        # Check if custom 404 page exists
        custom_404_path = os.path.join(os.getcwd(), '404.html')
        if os.path.exists(custom_404_path):
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(custom_404_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            # Fallback to default 404 message
            self.send_error(404, "File not found")

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