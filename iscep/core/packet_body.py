class PacketBody:
    def __init__(self, auth_token: str, body: dict[str, object]):
        self.auth_token = auth_token
        self.body = body

    def __str__(self):
        return f"{self.auth_token} {self.body}"
