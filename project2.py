import socket
import os
import sys
from datetime import datetime

# Server configuration
PORT = 8888  # Port range: 1024-65535

# Function to read HTML file contents
def read_html_file(filename):
    with open(filename, 'r') as file:
        return file.read()

# Function to log requests
def log_request(path, addr):
    if path != '/log':
        with open('log.txt', 'a') as log_file:
            log_file.write(f"{datetime.now()} - {addr[0]} requested {path}\n")

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

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', PORT))
serverSocket.listen(1)
print(f'Server running on port {PORT}')

while True:
    connectionSocket, addr = serverSocket.accept()
    request = connectionSocket.recv(1024).decode()
    #print(f'Received request: {request}')
    try:
        request_line = request.splitlines()[0]
        _, path, _ = request_line.split() #remove first and third element
        log_request(path, addr)#save the logged request to a file
        if path == "/":
            response = read_html_file('index.html')
        elif "color=red" in path:
            response = read_html_file('red.html')
        elif "color=green" in path:
            response = read_html_file('green.html')
        elif path == "/log":
            log_table_html = generate_log_table()
            headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
            response = f"<html><body><h1>Server Log</h1>{log_table_html}</body></html>"
        elif path == "/logdelete": # Delete the log file if it exists and return confirmation
            if os.path.exists('log.txt'):
                os.remove('log.txt')
                response = """<html><body><h1>Log Deleted Successfully</h1><a href="/">Go back</a></body></html>"""
        elif path == "/redapple.jpg": #Serve the redapple.jpg image
            with open('redapple.jpg', 'rb') as img:
                connectionSocket.send(b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n" + img.read())
            continue
        elif path == "/greenapple.jpg": #Serve the greenapple.jpg image
            with open('greenapple.jpg', 'rb') as img:
                connectionSocket.send(b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n" + img.read())
            continue
        else:
            response = read_html_file('404.html')

        if(response): connectionSocket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + response.encode())
        else: raise IOError()

    except IOError:
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 NotFound</h1></body></html>\r\n".encode())
        connectionSocket.close()

serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data
