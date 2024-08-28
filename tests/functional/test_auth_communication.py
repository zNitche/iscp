from iscep import Client, PacketType


def test_cmd_echo(client: Client, auth_server):
    res = client.send_command("test_cmd")
    assert res.type == PacketType.UNAUTHORIZED


def test_cmd_echo_auth(auth_client: Client, auth_server):
    cmd = "test_cmd"
    res = auth_client.send_command(cmd)

    assert res.type == PacketType.CMD_RESPONSE
    assert res.body.body == {"command": cmd}
