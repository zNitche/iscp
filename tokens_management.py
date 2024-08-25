import argparse
import os
from iscep import auth_management


def main(args):
    tokens_path: str = args.tokens_path
    add: bool = args.add
    remove: bool = args.remove
    owner: str | None = args.owner

    if add and owner:
        auth_management.add_token(owner, tokens_path)

    elif remove and owner:
        auth_management.remove_token(owner, tokens_path)


def get_args():
    parser = argparse.ArgumentParser()
    tokens_default_path = os.path.join(os.getcwd(), "tokens.json")

    parser.add_argument("--tokens_path",
                        type=str,
                        default=tokens_default_path,
                        help="tokens json path",
                        required=True)

    parser.add_argument("--add", action=argparse.BooleanOptionalAction,
                        type=bool, default=False, help="add auth token for owner", required=False)

    parser.add_argument("--remove", action=argparse.BooleanOptionalAction,
                        type=bool, default=False, help="remove auth token for owner", required=False)

    parser.add_argument("--owner",
                        type=str, default=None, help="owner of auth token, use with --add \ --remove", required=False)
    opt = parser.parse_args()

    return opt


if __name__ == '__main__':
    main(get_args())
