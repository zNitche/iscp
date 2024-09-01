import threading
import time
from tests import utils
from tests.mocks.tasks import TestTask
from iscep import Server, Client


def start_server(auth_enabled: bool = False, register_tasks: bool = False) -> tuple[Server, threading.Thread]:
    tokens_path = utils.get_tokens_path() if auth_enabled else None
    server = Server(auth_tokens_path=tokens_path, logging_enabled=False)

    if register_tasks:
        server.register_task(TestTask())

    thread = threading.Thread(target=server.run)
    thread.start()

    return server, thread


def stop_server(server: Server, thread: threading.Thread):
    server.stop()
    thread.join()


def get_client(auth_enabled: bool = False, creation_delay: float = 0.3) -> Client:
    # wait for server to start
    time.sleep(creation_delay)
    token = utils.get_test_auth_token() if auth_enabled else None

    return Client(addr="127.0.0.1", port=8989, auth_token=token)
