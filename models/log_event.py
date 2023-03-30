import uuid
import time


class LogEvent():
    def __init__(self, level: str, message: str, created_at: int, author_id: int, author_name: str):
        self.level = level
        self.message = message
        self.created_at = created_at
        self.author_id = author_id
        self.author_name = author_name
