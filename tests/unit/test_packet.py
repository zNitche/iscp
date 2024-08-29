from iscep.core.packet import Packet
from tests.mocks import mocks


def test_load_packet():
    packet = Packet.load(mocks.PACKET_BUFF)

    assert packet.type == mocks.PACKET.type
    assert packet.content == mocks.PACKET.content


def test_dump_packet():
    packet_buff = mocks.PACKET.dump()

    assert packet_buff == mocks.PACKET_RAW_BUFF
