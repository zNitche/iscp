from dataclasses import dataclass


@dataclass
class PacketBody:
    auth_token: str
    body: dict[str, object]

    def __str__(self):
        return f"is auth: {self.auth_token is not None} {self.body}"
