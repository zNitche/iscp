import secrets
import json
import os


def generate_token(nbytes_length=256):
    return secrets.token_hex(nbytes_length)


def get_tokens(file_path: str) -> dict[str, str]:
    with open(file_path, "r") as file:
        current_content = json.loads(file.read())

    return current_content


def create_empty_file(file_path: str):
    with open(file_path, "w+") as file:
        file.write(json.dumps({}))


def add_token(owner: str, tokens_path: str):
    if not os.path.exists(tokens_path):
        create_empty_file(tokens_path)

    tokens = get_tokens(tokens_path)

    if owner in tokens.keys():
        print(f"token for {owner} already exists, overwriting")

    tokens[owner] = generate_token(256)

    with open(tokens_path, "w") as file:
        file.write(json.dumps(tokens, indent=4))
        print("token has been saved successfully")


def remove_token(owner: str, tokens_path: str):
    file_exists = os.path.exists(tokens_path)

    if file_exists:
        tokens = get_tokens(tokens_path)

        if owner not in tokens.keys():
            print(f"token for {owner} doesn't exist")

        else:
            del tokens[owner]
            print("token has been removed successfully")

            with open(tokens_path, "w") as file:
                file.write(json.dumps(tokens, indent=4))

    else:
        print(f"{tokens_path} doesn't exist")
