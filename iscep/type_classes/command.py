from dataclasses import dataclass


@dataclass
class Command:
    name: str
    args: dict[str, any] | None = None
