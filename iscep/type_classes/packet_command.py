from dataclasses import dataclass


@dataclass
class PacketCommand:
    name: str
    args: dict[str, any] | None = None
