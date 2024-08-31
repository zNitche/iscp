from iscep import Task


class TestTask(Task):
    def __init__(self):
        super().__init__("test_task")

    def module(self, message: str, numb: int):
        return {"message": f"echo {message}", "numb": numb}
