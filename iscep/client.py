import socket
import ssl
from iscep.utils import communication
from iscep.core.packet import Packet, PacketType
from iscep.type_classes.packet_body import PacketBody
from iscep.utils.logger import Logger


class Client:
    def __init__(self,
                 addr: str,
                 port: int,
                 auth_token: str | None = None,
                 timeout: int = 10,
                 debug: bool = False,
                 ssl_cert_file: str | None = None):

        self.addr = addr
        self.port = port

        self.auth_token = auth_token

        self.debug = debug

        self.__ssl_cert_file = ssl_cert_file
        self.__ssl_context: ssl.SSLContext | None = None

        self.__logger = Logger(debug=debug, logger_name="client_logger")

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(timeout)

    def __enter__(self):
        self.__setup_ssl()

        self.__socket.connect((self.addr, self.port))
        self.__logger.debug(f"connected to {self.addr}:{self.port}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__send_close_connection_package()

        self.__socket.close()
        self.__logger.debug(f"disconnected from {self.addr}:{self.port}")

    def __setup_ssl(self):
        if self.__ssl_cert_file and os.path.exists(self.__ssl_cert_file):
            self.__ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.__ssl_context.load_verify_locations(self.__ssl_cert_file)
            self.__ssl_context.check_hostname = False

            self.__socket = self.__ssl_context.wrap_socket(self.__socket)

            self.__logger.debug(f"SSL has been enabled")

    def __send_close_connection_package(self):
        pbody = PacketBody(auth_token=self.auth_token, body={})
        packet = Packet(body=pbody, ptype=PacketType.CLOSE_CONNECTION)
        self.__socket.sendall(packet.dump())

    def send_command(self, command: str, non_auth: bool = False) -> Packet | None:
        self.__logger.debug(f"sending cmd...")

        auth_token = self.auth_token if not non_auth else None
        pbody = PacketBody(auth_token=auth_token, body={"command": command})

        packet = Packet(body=pbody, ptype=PacketType.SEND_CMD)

        self.__socket.sendall(packet.dump())
        self.__logger.debug(f"cmd has been sent, waiting for response...")

        res = communication.load_packet(self.__socket)

        return res


if __name__ == '__main__':
    import time
    import os

    auth_token = os.getenv("AUTH_TOKEN", None)

    with Client(addr="127.0.0.1", port=8989, debug=True, auth_token=auth_token, ssl_cert_file="../cert.pem") as client:
        response = client.send_command("test_cmd")
        time.sleep(5)
        response2 = client.send_command("test_cmd2")

        client.send_command("test_cmd non auth", non_auth=True)

        print(f"r1: {response.body}")
        print(f"r2: {response2.body}")
