import socket


def main():

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()  # wait for client
    connection.send("HTTP/1.1 200 OK\r\n\r\n".encode())
    connection.close()
    server_socket.close()


if __name__ == "__main__":
    main()
