from dataclasses import dataclass
from iscep.core.packet import PacketType


@dataclass
class CommandResponse:
    type: PacketType
    response: object | None = None
    error: str | None = None
