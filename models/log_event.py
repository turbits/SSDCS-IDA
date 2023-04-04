from utility.enums import LogMode, LogLevel, LogEndpoint


class LogEvent():
    def __init__(self, mode: LogMode, endpoint: LogEndpoint, level: LogLevel, message: str, created_at: int, author_id: int, author_name: str, is_endpoint: bool = False):
        self.mode = mode
        self.endpoint = endpoint
        self.level = level
        self.message = message
        self.created_at = created_at
        self.author_id = author_id
        self.author_name = author_name
        self.is_endpoint = is_endpoint

    def __str__(self):
        return f"LogEvent(mode={self.mode}, level={self.level}, message={self.message}, created_at={self.created_at}, author_id={self.author_id}, author_name={self.author_name})"

    def log_endpoint_hit(self):
        if self.is_endpoint:
            print(f"🎯[{self.mode}]{self.endpoint}")

    def log_event(self):

        # get time in human readable
        _time = datetime.datetime.fromtimestamp(self.created_at).strftime('%Y-%m-%d %H:%M:%S')

        # log an endpoint being hit
        if self.mode is LogMode.INFO and self.is_endpoint is True:
            self.log_endpoint_hit()

        # logging of debug and info events
        if self.mode == LogMode.DEBUG:
            print(f"🐞[DEBUG{_time}]:{self.message}")
        if self.mode == LogMode.INFO:
            print(f"🔵[INFO|{_time}]:{self.message}")

        # logging of application events
        
        # getting level symbol
        if self.level is not LogLevel.TEST:
            _symbol = ""
            if self.level is LogLevel.INFO:
                _symbol = "🔵"
            if self.level is LogLevel.ERROR or self.level is LogLevel.CRITICAL:
                _symbol = "🔴"
            if self.level is LogLevel.OK:
                _symbol = "🟢"
            
            # DATABASE
            
            
            # INFO
            
            # ERROR
            
            # CRITICAL
