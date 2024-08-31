class Task:
    def __init__(self, name: str):
        self.name = name

    def module(self, *args, **kwargs):
        raise NotImplemented()

    def run(self, args: dict[str, any] | None = None) -> any:
        res = self.module(**args if args is not None else {})
        return res
