import hashlib
import json
from enum import Enum
from iscep.utils import communication
from iscep.type_classes.packet_content import PacketContent
from iscep.type_classes.packet_command import PacketCommand


class PacketType(Enum):
    ECHO = 0
    SEND_CMD = 1
    CMD_RESPONSE = 2
    CLOSE_CONNECTION = 3
    UNAUTHORIZED = 4
    ERROR = 5


class Packet:
    def __init__(self, content: PacketContent | None = None, type: PacketType = PacketType.SEND_CMD):
        self.type = type
        self.content = content

    @staticmethod
    def load(buff: bytes):
        buff_size = len(buff)

        hash_length = 32
        packet_type_length = 2

        if buff_size <= hash_length + packet_type_length:
            raise Exception(f"packet buff size too small, expected ath least 36 bytes, got {buff_size}")

        packet_type = communication.int_from_bytes(buff[:packet_type_length])

        body_size = buff_size - hash_length
        body = buff[packet_type_length:body_size]

        packet_checksum = buff[body_size:].decode()
        body_checksum = hashlib.md5(body).hexdigest()

        if not body_checksum == packet_checksum:
            raise Exception(f"packet checksum missmatch, expected: '{packet_checksum}' got '{body_checksum}'")

        content = PacketContent(**json.loads(body.decode()))

        return Packet(content=content, type=PacketType(packet_type))

    @staticmethod
    def get_error_packet(message: str | None = None):
        content = PacketContent(error=message if message is not None else None)
        return Packet(type=PacketType.ERROR, content=content)

    @staticmethod
    def get_cmd_response_packet(response: any):
        content = PacketContent(response=response)
        return Packet(type=PacketType.CMD_RESPONSE, content=content)

    def dump(self) -> bytes:
        body = self.content.dump() if self.content else {}
        body_buff = json.dumps(body).encode()

        checksum = hashlib.md5(body_buff).hexdigest().encode()
        type = communication.int_to_bytes(self.type.value, length=2)

        content = type + body_buff + checksum
        size = communication.int_to_bytes(len(content))

        return size + content

    def get_command(self) -> PacketCommand | None:
        if self.content is None or self.content.command is None:
            return None

        return PacketCommand(name=self.content.command, args=self.content.args)

    def __str__(self):
        return f"{self.type.name} {self.content}"
