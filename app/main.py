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


def send_response(conn: socket.socket, status: int):

    conn.send(bytes(f"HTTP/1.1 {status} OK\r\n\r\n", "utf-8"))


def main():

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()  # wait for client

    data = connection.recv(1024)
    req = parse_request(data)
    print(req)

    if req.path == "/":
        send_response(connection, 200)
    else:
        send_response(connection, 404)

    connection.close()
    server_socket.close()


if __name__ == "__main__":
    main()
