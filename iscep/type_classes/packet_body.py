from dataclasses import dataclass


@dataclass
class PacketBody:
    auth_token: str | None
    body: dict[str, object] | None

    def __str__(self):
        auth_token = f'{self.auth_token[:5]}...' if self.auth_token is not None else None
        return f"auth: {auth_token} {self.body}"
