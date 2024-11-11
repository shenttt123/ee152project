import socket
import os
from datetime import datetime

# Server configuration
HOST = 'localhost'
PORT = 8080  # Port range: 1024-65535

# Function to read HTML file contents
def read_html_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None

# Function to log requests
def log_request(path, client_address):
    if path != '/log':
        with open('log.txt', 'a') as log_file:
            log_file.write(f"{datetime.now()} - {client_address[0]} requested {path}\n")

# Function to generate HTML table from log file
def generate_log_table():
    try:
        with open('log.txt', 'r') as log_file:
            log_entries = log_file.readlines()
        table_html = "<table border='1'><tr><th>Timestamp</th><th>Client IP</th><th>Request Path</th></tr>"
        for entry in log_entries:
            timestamp, rest = entry.split(" - ")
            client_ip, path = rest.split(" requested ")
            table_html += f"<tr><td>{timestamp}</td><td>{client_ip}</td><td>{path.strip()}</td></tr>"
        table_html += "</table>"
        return table_html
    except FileNotFoundError:
        return "<p>No log entries found.</p>"

# Start server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f'Server running on http://{HOST}:{PORT}')

    while True:
        # Wait for a client connection
        client_socket, client_address = server_socket.accept()
        with client_socket:
            # Receive request
            request = client_socket.recv(1024).decode()
            print(f'Received request: {request}')

            # Parse the request line
            try:
                request_line = request.splitlines()[0]
                _, path, _ = request_line.split()
            except ValueError:
                client_socket.sendall("HTTP/1.1 400 Bad Request\r\n\r\n".encode())
                continue

            # Log request
            log_request(path, client_address)

            # Routing based on URL path
            if path == "/":
                response = read_html_file('index.html')
            elif "color=red" in path:
                response = read_html_file('red.html')
            elif "color=green" in path:
                response = read_html_file('green.html')
            elif path == "/log":
                log_table_html = generate_log_table()
                headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
                response_body = f"<html><body><h1>Server Log</h1>{log_table_html}</body></html>"

                # Send headers and body separately or as a single encoded string
                client_socket.sendall(headers.encode() + response_body.encode())

            elif path == "/logdelete":
                # Delete the log file if it exists and return confirmation
                if os.path.exists('log.txt'):
                    os.remove('log.txt')
                    response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                                              <html><body><h1>Log Deleted Successfully</h1><a href="/">Go back</a></body></html>"""
                else:
                    response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                                              <html><body><h1>No Log to Delete</h1><a href="/">Go back</a></body></html>"""
            elif path == "/redapple.jpg":
                # Serve the redapple.jpg image
                with open('redapple.jpg', 'rb') as img:
                    client_socket.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n" + img.read())
                continue
            elif path == "/greenapple.jpg":
                # Serve the greenapple.jpg image
                with open('greenapple.jpg', 'rb') as img:
                    client_socket.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n" + img.read())
                continue
            else:
                response = read_html_file('404.html')

            # Send HTML response if available
            if response:
                client_socket.sendall("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + response.encode())
            else:
                client_socket.sendall("HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n".encode())
                client_socket.sendall("<html><body><h1>404 Not Found</h1></body></html>".encode())
