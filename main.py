from iscep import Server


if __name__ == "__main__":
    server = Server(port=8989, debug=True, logs_path="logs")

    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
