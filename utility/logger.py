import uuid
from datetime import datetime
import time
from models.log_event import LogEvent
from utility.enums import LogMode, LogEndpoint, LogLevel


# Logger should log events both to the server console and to the database


# logger.create(logevent)
def create(logevent):
    pass


def endpoint_hit(endpoint: LogEndpoint, mode: LogMode, param_and_type: str = None):
    _datetime = datetime.fromtimestamp(int(time.time()))
    _endpoint = endpoint.name.lower()

    if param_and_type is not None:
        print(f"🎯[{mode.name}|{_endpoint}/<{param_and_type}>] ({_datetime})")
    else:
        print(f"🎯[{mode.name}|{_endpoint}] ({_datetime})")
