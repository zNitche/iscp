import socket
from iscep import communication
from iscep.core import Packet
from iscep.logger import Logger


class Client:
    def __init__(self, addr: str, port: int, timeout: int = 10, debug: bool = False):
        self.addr = addr
        self.port = port

        self.debug = debug

        self.__logger = Logger(debug=debug)

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(timeout)

    def __enter__(self):
        self.__socket.connect((self.addr, self.port))
        self.__logger.debug(f"connected to {self.addr}:{self.port}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__socket.close()
        self.__logger.debug(f"disconnected from {self.addr}:{self.port}")

    def send_command(self, command: str) -> Packet | None:
        packet = Packet(body={
            "command": command,
        })

        self.__socket.sendall(packet.dump())
        res = communication.load_packet(self.__socket)

        return res


if __name__ == '__main__':
    with Client(addr="127.0.0.1", port=8989, debug=True) as client:
        response = client.send_command("test_cmd")

        print(response.body)
