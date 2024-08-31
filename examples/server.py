from iscep import Server
from examples.tasks import ExampleTask


if __name__ == "__main__":
    server = Server(port=8989,
                    debug=True,
                    logs_path="../logs",
                    auth_tokens_path="../tokens.json",
                    ssl_key_file="../key.pem",
                    ssl_cert_file="../cert.pem")

    try:
        server.register_task(ExampleTask())

        server.run()
    except KeyboardInterrupt:
        server.stop()
