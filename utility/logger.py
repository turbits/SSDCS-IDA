import uuid
from datetime import datetime
import time
from models.log_event import LogEvent
from utility.enums import LogMode, LogEndpoint, LogLevel


# Logger should log events both to the server console and to the database


# logger.create(logevent)
def create(logevent):
    pass


def endpoint_hit(endpoint: LogEndpoint, mode: LogMode):
    _datetime = datetime.fromtimestamp(int(time.time()))
    print(f"🎯[{mode.name}|{_datetime}]/{endpoint.name}")
