import threading
from tests import utils
from iscep import Server, Client


def start_server(auth_enabled: bool = False) -> tuple[Server, threading.Thread]:
    tokens_path = utils.get_tokens_path() if auth_enabled else None
    server = Server(auth_tokens_path=tokens_path, logging_enabled=False)

    thread = threading.Thread(target=server.run)
    thread.start()

    return server, thread


def stop_server(server: Server, thread: threading.Thread):
    server.stop()
    thread.join()


def get_client(auth_enabled: bool = False) -> Client:
    token = utils.get_test_auth_token() if auth_enabled else None

    return Client(addr="127.0.0.1", port=8989, auth_token=token)
