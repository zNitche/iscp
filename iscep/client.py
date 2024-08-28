import socket
import ssl
import os
from iscep.utils import communication
from iscep.core.packet import Packet, PacketType
from iscep.type_classes.packet_body import PacketBody
from iscep.utils.logger import Logger


class Client:
    def __init__(self,
                 addr: str,
                 port: int,
                 auth_token: str | None = None,
                 timeout: int = 5,
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
        try:
            self.__send_close_connection_package()
        except:
            self.__logger.exception("error while shutting down connection")

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
        packet = Packet(body=pbody, type=PacketType.CLOSE_CONNECTION)

        self.__socket.sendall(packet.dump())

    def send_command(self, command: str, non_auth: bool = False) -> Packet | None:
        self.__logger.debug(f"sending cmd...")

        auth_token = self.auth_token if not non_auth else None
        pbody = PacketBody(auth_token=auth_token, body={"command": command})
        packet = Packet(body=pbody, type=PacketType.SEND_CMD)

        try:
            self.__socket.sendall(packet.dump())
            self.__logger.debug(f"cmd has been sent, waiting for response...")

            res = communication.load_packet(self.__socket)

            return res

        except Exception as e:
            self.__logger.debug(f"error while sending command: {str(e)}")
