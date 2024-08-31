from iscep import Client
from iscep.core.packet import PacketType


def test_cmd_echo(client: Client, server):
    res = client.send_echo("echo")

    assert res.type == PacketType.ECHO
    assert res.content.response == {"echo": "echo"}
