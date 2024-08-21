import hashlib
import json


class Packet:
    def __init__(self, body: dict[str, str | int | None]):
        self.body = body

    @staticmethod
    def load(size: int, buff: bytes):
        # 32 bytes = length of md5 hash
        body_size = size - 32

        body = buff[:body_size]
        packet_checksum = buff[body_size:].decode()

        body_checksum = hashlib.md5(body).hexdigest()

        if not body_checksum == packet_checksum:
            raise Exception(f"packet checksum missmatch, expected: '{packet_checksum}' got '{body_checksum}'")

        body = json.loads(body.decode())

        return Packet(body=body)

    def dump(self) -> bytes:
        body_buff = json.dumps(self.body).encode()
        checksum = hashlib.md5(body_buff).hexdigest().encode()

        content = body_buff + checksum
        size = len(content).to_bytes(length=4, byteorder="big")

        return size + content
