import os
import socket
import threading
import argparse
from typing import Union
from dataclasses import dataclass

NoneType = type(None)


@dataclass
class Request:
    method: str
    path: str
    protocol: str
    host: str
    user_agent: str
    content_length: Union[str, NoneType]
    content_application: Union[str, NoneType]
    content: Union[list, NoneType]


def parse_request(data: bytes) -> Request:
    data = data.decode()
    http_request = data.split('\r\n')
    header = http_request[0].split(' ')
    method = header[0]
    path = header[1]
    protocol = header[2]
    host = http_request[1].lower().lstrip('host: ')
    user_agent = http_request[2].lower().lstrip('user-agent: ')

    content_length = None
    content_application = None
    content = None
    if 'POST' == method:
        content_length = http_request[4].lower().lstrip('content-length: ')
        content_application = http_request[5].lower().lstrip('content-type: ')
        content = http_request[7:]

    return Request(
        method=method,
        path=path,
        protocol=protocol,
        host=host,
        user_agent=user_agent,
        content_length=content_length,
        content_application=content_application,
        content=content,
    )


def send_get_response(conn: socket.socket, request: Request, directory: str):

    path = request.path
    user_agent = request.user_agent

    if path == "/":
        status = 200
        conn.send(bytes(f"HTTP/1.1 {status} OK\r\n\r\n", "utf-8"))
    elif path == "/user-agent":
        status = 200
        conn.send(bytes(f"HTTP/1.1 {status} OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}\r\n", "utf-8"))
    elif '/echo/' in path:
        status = 200
        text = path.replace('/echo/', '')
        conn.send(bytes(f"HTTP/1.1 {status} OK\r\nContent-Type: text/plain\r\nContent-Length: {len(text)}\r\n\r\n{text}\r\n", "utf-8"))
    elif directory and path.startswith('/files/'):
        file = path.split('/')[-1]
        if os.path.exists(f'{directory}/{file}'):
            text = None
            with open(f'{directory}/{file}') as f:
                text = f.read()
            status = 200
            conn.send(bytes(f"HTTP/1.1 {status} OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(text)}\r\n\r\n{text}\r\n", "utf-8"))
        else:
            status = 404
            conn.send(bytes(f"HTTP/1.1 {status} Not Found\r\n\r\n", "utf-8"))
    else:
        status = 404
        conn.send(bytes(f"HTTP/1.1 {status} Not Found\r\n\r\n", "utf-8"))


def send_post_response(conn, request, directory):
    path = request.path
    content = request.content
    if directory and path.startswith('/files/'):
        file = path.split('/')[-1]
        with open(f'{directory}/{file}', 'w') as f:
            for line in content:
                f.write(line)
        status = 201
        conn.send(bytes(f"HTTP/1.1 {status} Created\r\n\r\n", "utf-8"))
        return
    status = 404
    conn.send(bytes(f"HTTP/1.1 {status} Not Found\r\n\r\n", "utf-8"))


def validate_directory(directory):
    if not os.path.isdir(directory):
        raise ValueError("Directory not found")


def generate_response(connection, directory):
    data = connection.recv(1024)
    req = parse_request(data)
    print(req)
    if req.method == "GET":
        send_get_response(connection, req, directory)
    elif req.method == "POST":
        send_post_response(connection, req, directory)
    connection.close()


def main():

    directory = parse_arg()
    if directory:
        validate_directory(directory)
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept()  # wait for client
        client_thread = threading.Thread(target=generate_response, args=(connection, directory))
        client_thread.start()

    server_socket.close()


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=str, required=False)
    args = parser.parse_args()
    return args.directory if args.directory else None


if __name__ == "__main__":

    main()
