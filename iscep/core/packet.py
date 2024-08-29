import hashlib
import json
from enum import Enum
from iscep.utils import communication
from iscep.type_classes.packet_content import PacketContent


class PacketType(Enum):
    ECHO = 0
    SEND_CMD = 1
    CMD_RESPONSE = 2
    CLOSE_CONNECTION = 3
    UNAUTHORIZED = 4
    ERROR = 5


class Packet:
    def __init__(self, content: PacketContent = None, type: PacketType = PacketType.SEND_CMD):
        self.type = type
        self.content = content if content is not None else PacketContent()

    @staticmethod
    def load(buff: bytes):
        buff_size = len(buff)

        # 32 bytes = length of md5 hash
        # 4 bytes = packet type

        if buff_size <= 36:
            raise Exception(f"packet buff size too small, expected ath least 36 bytes, got {buff_size}")

        packet_type = communication.int_from_bytes(buff[:4])

        body_size = buff_size - 32
        body = buff[4:body_size]

        packet_checksum = buff[body_size:].decode()
        body_checksum = hashlib.md5(body).hexdigest()

        if not body_checksum == packet_checksum:
            raise Exception(f"packet checksum missmatch, expected: '{packet_checksum}' got '{body_checksum}'")

        content = PacketContent(**json.loads(body.decode()))

        return Packet(content=content, type=PacketType(packet_type))

    def dump(self) -> bytes:
        body_buff = json.dumps(self.content.__dict__).encode()
        checksum = hashlib.md5(body_buff).hexdigest().encode()
        type = communication.int_to_bytes(self.type.value)

        content = type + body_buff + checksum
        size = communication.int_to_bytes(len(content))

        return size + content

    @staticmethod
    def get_error_package(message: str | None = None):
        content = PacketContent(body={"error": message} if message is not None else None)
        return Packet(type=PacketType.ERROR, content=content)

    def __str__(self):
        return f"{self.type.name} {self.content}"
