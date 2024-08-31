from iscep import Task
import time


class ExampleTask(Task):
    def __init__(self):
        super().__init__("example_task")

    def module(self, message: str):
        time.sleep(2)
        return f"echo {message}"
