import socket
import threading
import selectors
import time
from iscep.utils import communication
from iscep.core.packet import PacketType, Packet
from iscep.utils.logger import Logger


class RequestsHandler:
    def __init__(self,
                 auth_token: str,
                 connection: socket.socket,
                 thread: threading.Thread,
                 timeout: int = 5,
                 poll_interval: float = 0.5):
        self.auth_token = auth_token

        self.__thread = thread
        self.__connection = connection

        self.__poll_interval = poll_interval
        self.__timeout = timeout

        self.__logger = Logger(logger_name=f"requests_handler_logger_{thread.native_id}")

    def __is_authenticated(self, packet: Packet) -> bool:
        if packet.body.auth_token and packet.body.auth_token == self.auth_token:
            return True

        return False

    def handle(self):
        selector = selectors.PollSelector()
        last_action_time = 0

        with self.__connection:
            selector.register(self.__connection, selectors.EVENT_READ)
            ready = selector.select(self.__poll_interval)

            while True:
                current_loop_time = time.time()

                if ready:
                    packet = communication.load_packet(self.__connection)

                    if packet:
                        self.__logger.info(f"received packet: {packet}")
                        if not self.__is_authenticated(packet):
                            raise Exception("packet is not authenticated!")

                        if packet.ptype == PacketType.CLOSE_CONNECTION:
                            break

                        self.__connection.sendall(packet.dump())

                    last_action_time = time.time()

                if last_action_time - current_loop_time >= self.__timeout:
                    break
