from iscep import Packet, PacketType
from iscep.type_classes import PacketContent


PACKET_BUFF = b'\x00\x01{"auth_token": null, "command": "test_cmd", "args": null, "error": null, "response": null}68472b416c29960306f819285f7a473d'
PACKET_RAW_BUFF = b'\x00\x00\x00|' + PACKET_BUFF
PACKET = Packet(type=PacketType.SEND_CMD, content=PacketContent(command="test_cmd"))
