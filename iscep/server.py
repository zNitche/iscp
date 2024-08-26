import socket
import threading
import selectors
import os
from iscep.utils.logger import Logger
from iscep.core.requests_handler import RequestsHandler


class Server:
    def __init__(self,
                 address: str = "127.0.0.1",
                 port: int = 8989,
                 poll_interval: float = 0.5,
                 timeout: int = 5,
                 thread_timeout: int = 10,
                 thread_socket_timeout: int = 120,
                 threads_cap: int = 4,
                 logs_path: str | None = None,
                 debug: bool = False,
                 auth_tokens_path: str | None = None):

        self.address = address
        self.port = port

        self.timeout = timeout
        self.thread_timeout = thread_timeout
        self.thread_socket_timeout = thread_socket_timeout
        self.poll_interval = poll_interval

        self.auth_tokens_path = auth_tokens_path
        self.require_auth = False
        self.debug = debug

        self.threads_cap = threads_cap
        self.__threads: list[threading.Thread] = []

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__selector = selectors.PollSelector

        self.__logger = Logger(logger_name="server_logger", debug=debug)
        self.__access_logger = Logger(logger_name="server_access_logger",
                                      logs_path=logs_path, logs_filename="access.log")
        self.__error_logger = Logger(logger_name="server_error_logger",
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
            handler = RequestsHandler(require_auth=self.require_auth,
                                      auth_tokens_path=self.auth_tokens_path,
                                      connection=conn,
                                      timeout=self.thread_timeout,
                                      poll_interval=self.poll_interval)
            handler.handle()

        except:
            self.__error_logger.exception(f"error while processing request, addr: {addr}, thread: {cur_thread.name}")

        finally:
            self.__threads.remove(cur_thread)
            self.__logger.info(f"closed connection with: {addr}, thread: {cur_thread.name} / {cur_thread.native_id}")

    def __mainloop(self):
        with self.__selector() as selector:
            selector.register(self.__socket, selectors.EVENT_READ)

            while True:
                ready = selector.select(self.poll_interval)

                if ready:
                    try:
                        conn, addr = self.__socket.accept()
                        self.__access_logger.info(f"connection from {addr}")

                        if len(self.__threads) < self.threads_cap - 1:
                            # just in case request handler became stuck somehow
                            conn.settimeout(self.thread_socket_timeout)

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

        if self.auth_tokens_path:
            if os.path.exists(self.auth_tokens_path):
                self.require_auth = True
                self.__logger.info(f"only authenticated Packets will be accepted")
            else:
                self.__logger.warning("auth tokens file doesn't exist, all packets will be accepted")

        self.__mainloop()

    def stop(self):
        self.__socket.close()

        for thread in self.__threads:
            thread.join()
