import socketserver
import threading


class RequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def handle(self):
        data = str(self.request.recv(1024), "utf-8")

        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, data), "utf-8")

        self.request.sendall(response)
