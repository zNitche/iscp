import socket
from iscep.core.packet import Packet


def receive(conn: socket.socket, length: int, raise_exception: bool = False) -> bytes:
    data = conn.recv(length)

    if raise_exception and (len(data) < length):
        raise Exception(f"receive length missmatch, requested {length}, got {len(data)}")

    return data


def load_packet(conn: socket.socket) -> Packet | None:
    size_buff = receive(conn=conn, length=4)
    size = int_from_bytes(size_buff)

    if size == 0:
        return None

    packet_data = receive(conn, size)
    return Packet.load(packet_data)


def int_to_bytes(val: int, length: int = 4):
    return val.to_bytes(length, byteorder="big")


def int_from_bytes(buff: bytes):
    return int.from_bytes(buff, byteorder="big")
