from iscep import Packet, PacketType
from iscep.type_classes import PacketContent


PACKET_BUFF = b'\x00\x00\x00\x00{"auth_token": null, "body": {"command": "test_cmd"}}06140e8daea8b174ae8de4b71bd3601c'
PACKET_RAW_BUFF = b'\x00\x00\x00Y' + PACKET_BUFF
PACKET = Packet(type=PacketType.SEND_CMD, content=PacketContent(auth_token=None, body={"command": "test_cmd"}))
