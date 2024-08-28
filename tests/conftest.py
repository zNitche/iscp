import pytest
from tests.modules import start_server, stop_server, get_client


@pytest.fixture(scope="module")
def server():
    server, server_thread = start_server()
    yield
    stop_server(server, server_thread)


@pytest.fixture(scope="module")
def auth_server():
    server, server_thread = start_server(auth_enabled=True)
    yield
    stop_server(server, server_thread)


@pytest.fixture(scope="function")
def client():
    with get_client() as client:
        yield client


@pytest.fixture(scope="function")
def auth_client():
    with get_client(auth_enabled=True) as client:
        yield client
