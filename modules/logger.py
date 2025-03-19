import queue

class Logger:
    def __init__(self):
        self.log_queue = queue.Queue()

    def write(self, message: str):
        self.log_queue.put(message)

    def pick(self) -> list[str]:
        # queueに入っているログを配列で返す
        logs = []
        while not self.log_queue.empty():
            logs.append(self.log_queue.get())
        return logs
