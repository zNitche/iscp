from iscep import Client
from iscep.core.packet import PacketType


def test_cmd_echo(client: Client, server):
    cmd = "test_cmd"
    res = client.send_command(cmd)

    assert res.type == PacketType.CMD_RESPONSE
    assert res.content.body == {"command": cmd}
