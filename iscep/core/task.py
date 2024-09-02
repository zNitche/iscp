import inspect


class Task:
    def __init__(self, name: str):
        self.name = name

    def module(self, *args, **kwargs):
        raise NotImplemented()

    def get_module_args(self):
        args = {}
        inspect_data = inspect.signature(self.module).parameters

        for key, val in inspect_data.items():
            args[key] = val.annotation.__name__

        return args

    def run(self, args: dict[str, any] | None = None) -> any:
        res = self.module(**args if args is not None else {})
        return res
