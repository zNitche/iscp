import socket
import threading
import selectors
import os
import ssl
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
                 auth_tokens_path: str | None = None,
                 ssl_cert_file: str | None = None,
                 ssl_key_file: str | None = None,
                 logging_enabled: bool = True):

        self.address = address
        self.port = port

        self.logging_enabled = logging_enabled

        self.timeout = timeout
        self.thread_timeout = thread_timeout
        self.thread_socket_timeout = thread_socket_timeout
        self.poll_interval = poll_interval

        self.requests_handler: type(RequestsHandler) = RequestsHandler

        self.__auth_tokens_path = auth_tokens_path
        self.__ssl_cert_file = ssl_cert_file
        self.__ssl_key_file = ssl_key_file

        self.__ssl_context: ssl.SSLContext | None = None

        self.require_auth = False
        self.debug = debug

        self.threads_cap = threads_cap
        self.__threads: list[threading.Thread] = []

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__selector = selectors.PollSelector

        self.requested_shutdown = False

        self.__logger = Logger(logger_name="server_logger", debug=debug, enabled=logging_enabled)
        self.__access_logger = Logger(logger_name="server_access_logger",
                                      logs_path=logs_path, logs_filename="access.log",
                                      enabled=logging_enabled)
        self.__error_logger = Logger(logger_name="server_error_logger",
                                     logs_path=logs_path, logs_filename="error.log",
                                     enabled=logging_enabled)

    def __setup_socket(self):
        self.__setup_ssl()

        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.settimeout(self.timeout)

        self.__socket.bind((self.address, self.port))
        self.__socket.listen()

        self.__logger.info(f"Server listening on {self.address}:{self.port}")

    def __setup_ssl(self):
        if self.__ssl_cert_file and self.__ssl_key_file:
            if os.path.exists(self.__ssl_key_file) and os.path.exists(self.__ssl_cert_file):
                self.__ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                self.__ssl_context.load_cert_chain(certfile=self.__ssl_cert_file, keyfile=self.__ssl_key_file)

                self.__socket = self.__ssl_context.wrap_socket(self.__socket, server_side=True)
                self.__logger.info(f"SSL has been enabled")

    def __handle_request(self, conn: socket.socket, addr: str):
        cur_thread = threading.current_thread()

        try:
            handler = self.requests_handler(require_auth=self.require_auth,
                                            auth_tokens_path=self.__auth_tokens_path,
                                            connection=conn,
                                            timeout=self.thread_timeout,
                                            poll_interval=self.poll_interval,
                                            logging_enabled=self.logging_enabled)
            handler.handle()

        except:
            self.__error_logger.exception(f"error while processing connection, addr: {addr}, thread: {cur_thread.name}")

        finally:
            conn.close()

            self.__threads.remove(cur_thread)
            self.__logger.info(f"closed connection with: {addr}, thread: {cur_thread.name} / {cur_thread.native_id}")

    def __mainloop(self):
        with self.__selector() as selector:
            selector.register(self.__socket, selectors.EVENT_READ)

            while not self.requested_shutdown:
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
                        self.__error_logger.exception("error while handling connection")

    def run(self):
        self.__setup_socket()

        if self.__auth_tokens_path:
            if os.path.exists(self.__auth_tokens_path):
                self.require_auth = True
                self.__logger.info(f"only authenticated Packets will be processed")
            else:
                self.__logger.warning("auth tokens file doesn't exist, all packets will be processed")

        self.__mainloop()

    def stop(self):
        self.requested_shutdown = True

        self.__socket.shutdown(socket.SHUT_RDWR)
        self.__socket.close()

        for thread in self.__threads:
            thread.join()

        self.__logger.info(f"server has been stopped successfully")
