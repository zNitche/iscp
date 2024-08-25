import secrets
import json


def generate_token(nbytes_length=256):
    return secrets.token_hex(nbytes_length)


def get_tokens(file_path: str) -> dict[str, str]:
    with open(file_path, "r") as file:
        current_content = json.loads(file.read())

    return current_content


def create_empty_file(file_path: str):
    with open(file_path, "w+") as file:
        file.write(json.dumps({}))
