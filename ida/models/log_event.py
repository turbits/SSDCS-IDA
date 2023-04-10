from utility.enums import LogMode, LogLevel, LogEndpoint


class LogEvent():
    def __init__(self, mode: LogMode, endpoint: LogEndpoint, level: LogLevel, author_username: str, created_at: int, message: str = "", is_endpoint: bool = False):
        self.mode = mode
        self.endpoint = endpoint
        self.level = level
        self.message = message
        self.created_at = created_at
        self.author_username = author_username
        self.is_endpoint = is_endpoint

    def __str__(self):
        return f"LogEvent(mode={self.mode}, endpoint={self.endpoint}, level={self.level}, message={self.message}, created_at={self.created_at}, author_username={self.author_username})"
