import socket
import threading


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'utf-8'))
        response = str(sock.recv(1024), 'utf-8')

        print(f"Received {response}")


if __name__ == '__main__':
    addr = "127.0.0.1"
    port = 8989

    for i in range(5):
        t = threading.Thread(target=client, args=(addr, port, f"Hello World {i}"))
        t.start()
