import time
import os
from iscep import Client


if __name__ == '__main__':
    auth_token = os.getenv("AUTH_TOKEN", None)

    with Client(addr="127.0.0.1",
                port=8989,
                debug=True,
                auth_token=auth_token,
                ssl_cert_file="../cert.pem") as client:

        response = client.send_command("example_task", args={"message": "hello world"})
        # time.sleep(5)
        response2 = client.send_command("example_task")
        response3 = client.send_command("example_task", use_auth=False)

        print(f"r1: {response}")
        print(f"r2: {response2}")
        print(f"r3: {response3}")
