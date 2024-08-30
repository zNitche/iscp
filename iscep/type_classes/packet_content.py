from dataclasses import dataclass


@dataclass
class CommandSection:
    name: str | None = None
    args: dict[str, any] | None = None


@dataclass
class PacketContent:
    auth_token: str | None = None
    command: CommandSection | None = None
    response: object | None = None

    def __str__(self):
        auth_token = f'{self.auth_token[:5]}...' if self.auth_token is not None else None
        return f"auth: {auth_token} command: {self.command} response: {self.response}"
