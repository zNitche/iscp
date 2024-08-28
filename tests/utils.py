import os
import json
from tests import consts


def get_tokens_path() -> str | None:
    tokens_path = os.path.join(consts.MOCKS_PATH, "tokens.json")
    return tokens_path if os.path.exists(tokens_path) else None


def get_test_auth_token() -> str | None:
    tokens_path = get_tokens_path()

    if tokens_path is None:
        return None

    with open(tokens_path, "r") as file:
        data = json.loads(file.read())

    return data.get("user")
