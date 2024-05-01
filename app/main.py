import socket
from dataclasses import dataclass


@dataclass
class Request:
    method: str
    path: str
    protocol: str
    host: str


def parse_request(data: bytes) -> Request:
    data = data.decode()
    http_request = data.split('\r\n')
    header = http_request[0].split(' ')
    host = http_request[1].lower().lstrip('host: ')
    return Request(
        method=header[0],
        path=header[1],
        protocol=header[2],
        host=host
    )


def send_response(conn: socket.socket, path: str):

    if path == "/":
        status = 200
        conn.send(bytes(f"HTTP/1.1 {status} OK\r\n\r\n", "utf-8"))
    if '/echo/' in path:
        status = 200
        text = path.replace('/echo/', '')
        conn.send(bytes(f"HTTP/1.1 {status} OK\r\nContent-Type: text/plain\r\nContent-Length: {len(text)}\r\n\r\n{text}\r\n", "utf-8"))
    else:
        status = 404
        conn.send(bytes(f"HTTP/1.1 {status} Not Found\r\n\r\n", "utf-8"))


def main():

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()  # wait for client

    data = connection.recv(1024)
    req = parse_request(data)
    send_response(connection, req.path)
    connection.close()
    server_socket.close()


if __name__ == "__main__":
    main()
