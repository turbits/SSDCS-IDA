import uuid
import time


class LogEvent():
    def __init__(self, log_level, log_message):
        self.log_level = log_level
        self.log_message = log_message
        self.log_timestamp = int(time.time.now())
        self.log_id = str(uuid.uuid4())
