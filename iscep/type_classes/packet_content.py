from dataclasses import dataclass


@dataclass
class PacketContent:
    auth_token: str | None = None
    body: dict[str, object] | None = None

    def __str__(self):
        auth_token = f'{self.auth_token[:5]}...' if self.auth_token is not None else None
        return f"auth: {auth_token} {self.body}"
