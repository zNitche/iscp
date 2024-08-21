import socket
import threading
from iscep import communication
from iscep.core import Packet


def client(ip, port, packet):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))

        sock.sendall(packet.dump())

        p = communication.load_packet(sock)
        if p:
            print(f"Received {p.body}")


if __name__ == '__main__':
    addr = "127.0.0.1"
    port = 8989

    for i in range(5):
        data = {
            "test": i,
            "test2": True
        }

        packet = Packet(body=data)

        t = threading.Thread(target=client, args=(addr, port, packet))
        t.start()
