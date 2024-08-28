import hashlib
import json
from enum import Enum
from iscep.utils import communication
from iscep.type_classes.packet_body import PacketBody


class PacketType(Enum):
    SEND_CMD = 0
    CMD_RESPONSE = 1
    CLOSE_CONNECTION = 2
    UNAUTHORIZED = 3
    ERROR = 4


class Packet:
    def __init__(self, body: PacketBody = None, type: PacketType = PacketType.SEND_CMD):
        self.type = type
        self.body = body if body is not None else PacketBody()

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

        body = PacketBody(**json.loads(body.decode()))

        return Packet(body=body, type=PacketType(packet_type))

    def dump(self) -> bytes:
        body_buff = json.dumps(self.body.__dict__).encode()
        checksum = hashlib.md5(body_buff).hexdigest().encode()
        type = communication.int_to_bytes(self.type.value)

        content = type + body_buff + checksum
        size = communication.int_to_bytes(len(content))

        return size + content

    @staticmethod
    def get_error_package(message: str | None = None):
        body = PacketBody(body={"error": message} if message is not None else None)
        return Packet(type=PacketType.ERROR, body=body)

    def __str__(self):
        return f"{self.type.name} {self.body}"
