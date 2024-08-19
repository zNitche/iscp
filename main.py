from iscep.server import Server


if __name__ == "__main__":
    server = Server(logs_path="logs", port=8989)

    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
