from utility.enums import LogMode, LogLevel, LogEndpoint


class LogEvent():
    def __init__(self, mode: LogMode, endpoint: LogEndpoint, level: LogLevel, author_name: str, created_at: int, message: str = "", is_endpoint: bool = False):
        self.mode = mode
        self.endpoint = endpoint
        self.level = level
        self.message = message
        self.created_at = created_at
        self.author_name = author_name
        self.is_endpoint = is_endpoint

    def __str__(self):
        return f"LogEvent(mode={self.mode}, level={self.level}, message={self.message}, created_at={self.created_at}, author_name={self.author_name})"
