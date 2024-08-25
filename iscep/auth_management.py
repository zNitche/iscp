import json
import os
from iscep.utils import auth


def add_token(owner: str, tokens_path: str):
    if not os.path.exists(tokens_path):
        auth.create_empty_file(tokens_path)

    tokens = auth.get_tokens(tokens_path)

    if owner in tokens.keys():
        print(f"token for {owner} already exists, overwriting")

    tokens[owner] = auth.generate_token(256)

    with open(tokens_path, "w") as file:
        file.write(json.dumps(tokens, indent=4))
        print("token has been saved successfully")


def remove_token(owner: str, tokens_path: str):
    file_exists = os.path.exists(tokens_path)

    if file_exists:
        tokens = auth.get_tokens(tokens_path)

        if owner not in tokens.keys():
            print(f"token for {owner} doesn't exist")

        else:
            del tokens[owner]
            print("token has been removed successfully")

            with open(tokens_path, "w") as file:
                file.write(json.dumps(tokens, indent=4))

    else:
        print(f"{tokens_path} doesn't exist")
