import json
import time
from datetime import datetime
from flask import request
from utility.enums import LogMode, LogLevel, LogEndpoint


class LogEvent():
    def __init__(self, mode: LogMode, endpoint: LogEndpoint, level: LogLevel, message: str = "", author_id: int = 0, author_name: str = "SYSTEM", created_at: int = int(time.time()), is_endpoint: bool = False):
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

    def log_endpoint_hit(self, time):
        if self.is_endpoint:
            print(f"🎯[{self.mode.name}|{time}]{self.endpoint}")

    def log_event(self):
        # getting level symbol
        if self.level is LogLevel.TEST and self.mode is LogMode.DEBUG:
            _symbol = "🐞"
        if self.mode is LogMode.DATABASE:
            _symbol = "💽"
        if self.level is LogLevel.INFO:
            _symbol = "🔵"
        if self.level is LogLevel.OK:
            _symbol = "🟢"
        if self.level is LogLevel.ERROR:
            _symbol = "🟡"
        if self.level is LogLevel.CRITICAL:
            _symbol = "🔴"

        # get time in human readable format
        _time = datetime.fromtimestamp(self.created_at)

        # log an endpoint being hit
        if self.mode is LogMode.INFO and self.is_endpoint is True:
            self.log_endpoint_hit(_time)

        # if debug, only log to server console
        if self.mode is LogMode.DEBUG:
            print(f"{_symbol}[{self.mode.name}|{_time}]:{self.message}")
            return

        # log to server console
        print(f"{_symbol}[{self.mode.name}|{_time}]:{self.message}")

        # log to database
        try:
            request.post("http://localhost:8080/logs", data=json.dumps(self.__dict__), content_type="application/json")

            # # return response
            # return response(status=res.status_code, body=res.text)

            return

        except Exception as e:
            return self.log_event(LogEvent(LogMode.POST, LogEndpoint.LOGS, LogLevel.ERROR, {str(e)}, int(time.time()), 0, "IDA", False))
