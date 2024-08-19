import socketserver
from iscep.logger import Logger
from iscep.server.request_handler import RequestHandler


class Server(socketserver.ThreadingTCPServer):
    def __init__(self,
                 address: str = "127.0.0.1",
                 port: int = 8989,
                 logs_path: str | None = None,
                 timeout: int = 10):

        super().__init__(server_address=(address, port), RequestHandlerClass=RequestHandler)

        self.timeout = timeout
        self.request_queue_size = 3

        self.__logger = Logger(logger_name="server_logger")
        self.__access_logger = Logger(logger_name="socket_server_access_logger",
                                      logs_path=logs_path, logs_filename="access.log")
        self.__error_logger = Logger(logger_name="socket_server_error_logger",
                                     logs_path=logs_path, logs_filename="error.log")

    def process_request(self, request, client_address):
        self.__access_logger.info(f"request from {client_address}")
        super().process_request(request, client_address)

    def handle_error(self, request, client_address):
        self.__error_logger.exception(f"error while processing request from {client_address}")

    def run(self):
        self.__logger.info(f"server running at {self.server_address}")
        self.serve_forever()

    def stop(self):
        self.server_close()
        self.shutdown()
