from iscep import Client
from iscep.core.packet import PacketType


def test_command_not_found(client: Client, server_w_tasks):
    res = client.send_command("non_existing_task")

    assert res.type == PacketType.ERROR


def test_command(client: Client, server_w_tasks):
    res = client.send_command("test_task", args={"message": "hello", "numb": 1})

    assert res.type == PacketType.CMD_RESPONSE
    assert res.response == {"message": "echo hello", "numb": 1}
