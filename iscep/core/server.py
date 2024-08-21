import socket
import threading
import selectors
from iscep.logger import Logger
from iscep import communication


class Server:
    def __init__(self,
                 address: str = "127.0.0.1",
                 port: int = 8989,
                 poll_interval: float = 0.5,
                 timeout: int = 5,
                 threads_cap: int = 4,
                 logs_path: str | None = None,
                 debug: bool = False):

        self.address = address
        self.port = port

        self.timeout = timeout
        self.poll_interval = poll_interval

        self.debug = debug

        self.threads_cap = threads_cap
        self.__threads: list[threading.Thread] = []

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__selector = selectors.PollSelector()

        self.__logger = Logger(logger_name="server_logger", debug=debug)
        self.__access_logger = Logger(logger_name="socket_server_access_logger",
                                      logs_path=logs_path, logs_filename="access.log")
        self.__error_logger = Logger(logger_name="socket_server_error_logger",
                                     logs_path=logs_path, logs_filename="error.log")

    def __setup_socket(self):
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.settimeout(self.timeout)

        self.__socket.bind((self.address, self.port))
        self.__socket.listen()

        self.__logger.info(f"Server listening on {self.address}:{self.port}")

    def __handle_request(self, conn: socket.socket, addr: str):
        cur_thread = threading.current_thread()

        try:
            with conn:
                packet = communication.load_packet(conn)

                if packet:
                    conn.sendall(packet.dump())

        except:
            self.__error_logger.exception(f"error while processing request, addr: {addr}, thread: {cur_thread.name}")

        finally:
            self.__threads.remove(cur_thread)

    def __mainloop(self):
        with self.__selector as selector:
            selector.register(self.__socket, selectors.EVENT_READ)

            while True:
                ready = selector.select(self.poll_interval)

                if ready:
                    try:
                        conn, addr = self.__socket.accept()
                        self.__access_logger.info(f"connection from {addr}")

                        if len(self.__threads) < self.threads_cap - 1:
                            thread = threading.Thread(target=self.__handle_request, args=(conn, addr))
                            self.__logger.info(f"starting request handler: {thread.name}")

                            self.__threads.append(thread)
                            thread.start()
                        else:
                            conn.close()
                    except:
                        self.__error_logger.exception("error while handling request")

    def run(self):
        self.__setup_socket()
        self.__mainloop()

    def stop(self):
        self.__socket.close()

        for thread in self.__threads:
            thread.join()
