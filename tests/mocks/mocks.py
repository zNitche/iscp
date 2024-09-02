from iscep import Packet, PacketType
from iscep.type_classes import PacketContent


PACKET_BUFF = b'\x00\x02{"command": "test_cmd"}cc13d75d4a4ce43b1cc85d506ec5ed87'
PACKET_RAW_BUFF = b'\x00\x00\x009' + PACKET_BUFF
PACKET = Packet(type=PacketType.SEND_CMD, content=PacketContent(command="test_cmd"))
