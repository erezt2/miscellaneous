import os
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 4000))
server_socket.listen()

if not os.path.exists("C:\\PythonServerFile"):
    os.makedirs("C:\\PythonServerFile")

while True:
    (client_socket, client_address) = server_socket.accept()

    operation = client_socket.recv(1024).decode()

    if operation.split()[0] == "UPLOAD":
        file_path = "C:\\PythonServerFile\\" + ' '.join(operation.split()[1:])
        ending = "." + file_path.split(".")[-1]
        file_path = ".".join(file_path.split(".")[:-1])
        c = 1

        if os.path.exists(file_path + ending):
            c += 1

        while os.path.exists(file_path + str(c) + ending):
            c += 1

        if c != 1:
            f = open(file_path + str(c) + ending, 'wb')
        else:
            f = open(file_path + ending, 'wb')

        data = client_socket.recv(1024)

        while data:
            f.write(data)
            data = client_socket.recv(1024)

        f.close()
        client_socket.close()

    if operation.split()[0] == "DOWNLOAD":
        files = ''
        for filename in os.listdir("C:\\PythonServerFile"):
            f = os.path.join("C:\\PythonServerFile", filename)
            if os.path.isfile(f):
                files += filename
                files += "|"

        files += '/'
        client_socket.sendall(files.encode())

        data = client_socket.recv(1024).decode()

        if data:
            f = open(os.path.join("C:\\PythonServerFile", data), 'rb')
            content = f.read()
            f.close()
            client_socket.sendall(content)
        client_socket.close()
