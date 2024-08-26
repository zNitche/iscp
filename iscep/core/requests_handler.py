import socket
import threading
import selectors
import time
from iscep.utils import communication, auth
from iscep.core.packet import PacketType, Packet
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

        self.__logger = Logger(logger_name=f"requests_handler_logger_{self.__thread.native_id}")

    def __is_authenticated(self, packet: Packet) -> tuple[str | None, bool]:
        packet_token = packet.body.auth_token

        if packet_token:
            tokens = auth.get_tokens(self.auth_tokens_path)

            for token_owner in tokens.keys():
                if tokens[token_owner] == packet_token:
                    return token_owner, True

        return None, False

    def handle(self):
        last_action_time = 0

        with self.__selector() as selector:
            selector.register(self.__connection, selectors.EVENT_READ)

            while self.__connection:
                ready = selector.select(self.__poll_interval)
                current_loop_time = time.time()

                if ready:
                    packet = communication.load_packet(self.__connection)

                    if packet:
                        self.__logger.info(f"received packet")

                        if self.require_auth:
                            token_owner, is_authenticated = self.__is_authenticated(packet)
                            if not is_authenticated:
                                raise Exception("packet is not authenticated!")

                        self.__logger.info(f"processing packet {packet} by {token_owner}...")

                        if packet.ptype == PacketType.CLOSE_CONNECTION:
                            break

                        response_packet = self.__process(packet)
                        self.__connection.sendall(response_packet.dump())

                    last_action_time = time.time()

                if current_loop_time - last_action_time >= self.__timeout:
                    break

    def __process(self, packet: Packet) -> Packet:
        # processing goes here, for now its only packet echo
        return packet
