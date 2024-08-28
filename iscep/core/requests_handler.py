import socket
import threading
import selectors
import time
from iscep.utils import communication, auth
from iscep.core.packet import Packet, PacketType
from iscep.utils.logger import Logger


class RequestsHandler:
    def __init__(self,
                 connection: socket.socket,
                 require_auth: bool = False,
                 auth_tokens_path: str | None = None,
                 timeout: int = 5,
                 poll_interval: float = 0.5):

        self.require_auth = require_auth
        self.auth_tokens_path = auth_tokens_path

        self.__selector = selectors.PollSelector

        self.__thread = threading.current_thread()
        self.__connection = connection

        self.__poll_interval = poll_interval
        self.__timeout = timeout

        self.requested_shutdown = False

        self.__logger = Logger(logger_name=f"requests_handler_logger_{self.__thread.native_id}")

    def __is_authenticated(self, packet: Packet) -> tuple[str | None, bool]:
        packet_token = packet.content.auth_token

        if packet_token:
            tokens = auth.get_tokens(self.auth_tokens_path)

            for token_owner in tokens.keys():
                if tokens[token_owner] == packet_token:
                    return token_owner, True

        return None, False

    def __check_auth(self, packet: Packet) -> bool:
        if self.require_auth:
            token_owner, is_authenticated = self.__is_authenticated(packet)
            if not is_authenticated:
                self.__logger.info(f"received unauthorized packet, skipping...")
                return False

        return True

    def handle(self):
        self.__connection_loop()

        try:
            self.__connection.shutdown(socket.SHUT_RDWR)
        except:
            self.__logger.exception("error while shutting down socket connection")

    def __connection_loop(self):
        last_action_time = 0

        with self.__selector() as selector:
            selector.register(self.__connection, selectors.EVENT_READ)

            while self.__connection and not self.requested_shutdown:
                ready = selector.select(self.__poll_interval)
                current_loop_time = time.time()

                if ready:
                    packet = communication.load_packet(self.__connection)

                    if packet:
                        self.__logger.info(f"processing packet {packet}...")

                        response_packet = self.__process_packet(packet)
                        if response_packet:
                            self.__connection.sendall(response_packet.dump())

                        last_action_time = time.time()

                    else:
                        # stop processing if client closed connection
                        break

                if current_loop_time - last_action_time >= self.__timeout:
                    break

    def __process_cmd(self, packet: Packet) -> Packet:
        try:
            return Packet(type=PacketType.CMD_RESPONSE, content=packet.content)
        except Exception as e:
            return Packet.get_error_package(str(e))

    def __process_packet(self, packet: Packet) -> Packet | None:
        if not self.__check_auth(packet):
            return Packet(type=PacketType.UNAUTHORIZED)

        match packet.type:
            case PacketType.CLOSE_CONNECTION:
                self.requested_shutdown = True
                return None

            case PacketType.SEND_CMD:
                return self.__process_cmd(packet)

        return Packet.get_error_package()
