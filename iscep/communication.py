import socket
from iscep.core.packet import Packet


def receive(conn: socket.socket | None, length: int) -> bytes:
    data = conn.recv(length)

    if len(data) < length:
        raise Exception(f"receive length missmatch, requested {length}, got {len(data)}")

    return data


def load_packet(conn: socket.socket) -> Packet | None:
    size_buff = receive(conn=conn, length=4)
    size = int.from_bytes(size_buff, byteorder="big")

    if size == 0:
        return None

    packet_data = receive(conn, size)
    return Packet.load(packet_data)
