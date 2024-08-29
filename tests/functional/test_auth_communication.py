from iscep import Client, PacketType


def test_cmd_echo(client: Client, auth_server):
    res = client.send_command("echo")
    assert res.type == PacketType.UNAUTHORIZED


def test_cmd_echo_auth(auth_client: Client, auth_server):
    res = auth_client.send_echo("echo")

    assert res.type == PacketType.ECHO
    assert res.content.body == {"echo": "echo"}
