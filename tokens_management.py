import argparse
import os
from iscep import auth_management


def main(args):
    tokens_path: str = args.tokens_path
    add_token_owner: str = args.add
    remove_token_owner: str = args.remove

    if add_token_owner:
        auth_management.add_token(add_token_owner, tokens_path)

    elif remove_token_owner:
        auth_management.remove_token(remove_token_owner, tokens_path)


def get_args():
    parser = argparse.ArgumentParser()

    current_dir = os.path.abspath(os.path.dirname(__file__))
    tokens_default_path = os.path.join(current_dir, "tokens.json")

    parser.add_argument("--tokens-path",
                        type=str,
                        default=tokens_default_path,
                        help="tokens json path",
                        required=False)

    parser.add_argument("--add",
                        type=str, default=None, help="owner of auth token, to add", required=False)

    parser.add_argument("--remove",
                        type=str, default=None, help="owner of auth token, to remove", required=False)

    opt = parser.parse_args()

    return opt


if __name__ == '__main__':
    main(get_args())
