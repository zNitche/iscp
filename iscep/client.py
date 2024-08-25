import socket
from iscep.utils import communication
from iscep.core.packet import Packet, PacketType
from iscep.utils.logger import Logger


class Client:
    def __init__(self, addr: str, port: int, timeout: int = 10, debug: bool = False):
        self.addr = addr
        self.port = port

        self.debug = debug

        self.__logger = Logger(debug=debug, logger_name="client_logger")

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(timeout)

    def __enter__(self):
        self.__socket.connect((self.addr, self.port))
        self.__logger.debug(f"connected to {self.addr}:{self.port}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__send_close_connection_package()

        self.__socket.close()
        self.__logger.debug(f"disconnected from {self.addr}:{self.port}")

    def __send_close_connection_package(self):
        packet = Packet(body={}, ptype=PacketType.CLOSE_CONNECTION)
        self.__socket.sendall(packet.dump())

    def send_command(self, command: str) -> Packet | None:
        self.__logger.debug(f"sending cmd...")

        packet = Packet(body={
            "command": command,
        }, ptype=PacketType.SEND_CMD)

        self.__socket.sendall(packet.dump())
        self.__logger.debug(f"cmd has been sent, waiting for response...")

        res = communication.load_packet(self.__socket)

        return res


if __name__ == '__main__':
    import time

    with Client(addr="127.0.0.1", port=8989, debug=True) as client:
        response = client.send_command("test_cmd")
        time.sleep(4)
        response2 = client.send_command("test_cmd2")

        print(f"r1: {response.body}")
        print(f"r2: {response2.body}")
