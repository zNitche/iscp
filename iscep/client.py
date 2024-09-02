import socket
import ssl
import os
from iscep.utils import communication
from iscep.core.packet import Packet, PacketType
from iscep.type_classes.packet_content import PacketContent
from iscep.type_classes.command_response import CommandResponse
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
        self.__send_close_connection_packet()

        self.__socket.close()
        self.__logger.debug(f"disconnected from {self.addr}:{self.port}")

    def __setup_ssl(self):
        if self.__ssl_cert_file and os.path.exists(self.__ssl_cert_file):
            self.__ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.__ssl_context.load_verify_locations(self.__ssl_cert_file)
            self.__ssl_context.check_hostname = False

            self.__socket = self.__ssl_context.wrap_socket(self.__socket)

            self.__logger.debug(f"SSL has been enabled")

    def __send_close_connection_packet(self):
        self.__logger.debug(f"sending close connection packet...")

        content = PacketContent(auth_token=self.auth_token)
        packet = Packet(content=content, type=PacketType.CLOSE_CONNECTION)

        self.__send_packet(packet)

    def send_echo(self, message: str) -> Packet:
        self.__logger.debug(f"sending echo...")

        content = PacketContent(auth_token=self.auth_token, response={"echo": message})
        packet = Packet(content=content, type=PacketType.ECHO)

        return self.__send_packet(packet)

    def send_command(self,
                     name: str, args: dict[str, any] | None = None,
                     use_auth: bool = True) -> CommandResponse | None:

        self.__logger.debug(f"sending cmd...")

        auth_token = self.auth_token if use_auth else None

        content = PacketContent(auth_token=auth_token, command=name, args=args)
        packet = Packet(content=content, type=PacketType.SEND_CMD)

        response = self.__send_packet(packet)

        if response is None or response.content is None:
            return None

        return CommandResponse(type=response.type, response=response.content.response, error=response.content.error)

    def get_commands(self, use_auth: bool = True) -> dict[str, dict[str, object]] | None:
        self.__logger.debug(f"sending commands discover...")

        auth_token = self.auth_token if use_auth else None
        packet = Packet(type=PacketType.DISCOVER, content=PacketContent(auth_token=auth_token))

        response = self.__send_packet(packet)

        if response is None or response.content is None:
            return None

        return response.content.response

    def __send_packet(self, packet: Packet) -> Packet:
        response = None

        try:
            self.__socket.sendall(packet.dump())
            self.__logger.debug(f"packet has been sent...")

            response = communication.load_packet(self.__socket)

        except Exception as e:
            self.__logger.debug(f"error while sending packet: {str(e)}")

        return response
