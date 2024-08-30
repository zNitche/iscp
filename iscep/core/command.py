from typing import Callable


class Command:
    def __init__(self, name: str, module: Callable[[...], any]):
        self.name = name
        self.__module = module

    def run(self, args: dict[str, any]) -> any:
        res = self.__module(**args)
        return res
