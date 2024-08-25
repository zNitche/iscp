import hashlib
import json
from enum import Enum
from iscep.utils import communication
from iscep.type_classes.packet_body import PacketBody


class PacketType(Enum):
    SEND_CMD = 0
    CLOSE_CONNECTION = 1


class Packet:
    def __init__(self, body: PacketBody, ptype: PacketType = PacketType.SEND_CMD):
        self.ptype = ptype
        self.body = body

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

        return Packet(body=body, ptype=PacketType(packet_type))

    def dump(self) -> bytes:
        body_buff = json.dumps(self.body.__dict__).encode()
        checksum = hashlib.md5(body_buff).hexdigest().encode()
        type = communication.int_to_bytes(self.ptype.value)

        content = type + body_buff + checksum
        size = communication.int_to_bytes(len(content))

        return size + content

    def __str__(self):
        return f"{self.ptype.name} {self.body}"
