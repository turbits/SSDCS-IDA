import uuid
import time
from datetime import datetime
from models.log_event import LogEvent
from utility.enums import LogMode, LogEndpoint, LogLevel
from utility.db import connect_db, close_db
from utility.validate_data import validate_data

# Logger should log events both to the server console and to the database
# Unfortunately, the logger does not utilize the LogEvent class - but it should be extended to do so


SYSAUTHOR = "SYSTEM"


def endpoint_hit(endpoint: LogEndpoint, mode: LogMode, param_and_type: str = None):
    human_timestamp = datetime.fromtimestamp(int(time.time()))

    create_log(level=LogLevel.INFO, message=f"Endpoint hit: {str(endpoint.name).lower()}", author_username=SYSAUTHOR, is_system=False)

    if param_and_type is not None:
        print(f"🎯[{mode.name}|{endpoint.name.lower()}/<{param_and_type}>] ({human_timestamp})")
    else:
        print(f"🎯[{mode.name}|{endpoint.name.lower()}] ({human_timestamp})")
    return


# Because LogEvents are meant to be immutable, i.e. they are read only by anyone except the system, we will not implement create, update, or delete endpoints for LogEvents.
# Instead, the logger will use an internal function (create_log) to create LogEvents
# the only endpoints that will be exposed are GET endpoints to fetch all LogEvents or a single LogEvent by id. see routes/logs.py
def create_log(level: LogLevel, message: str, author_username: str, is_system=False):
    unix_timestamp = int(time.time())
    human_timestamp = datetime.fromtimestamp(unix_timestamp)

    con, cursor = connect_db()

    try:
        # combine log data into a dict
        # created_at is initialized to the current unix timestamp; we can use `datetime.datetime.fromtimestamp(<timestamp>)` to convert it to a human readable datetime
        log_data = {
            "level": level,
            "message": message,
            "created_at": unix_timestamp,
            "author_username": author_username,
        }

        # validate the logevent using the LogEvent model and the data above, passed through a generic validation function
        validation_check = validate_data(log_data, LogEvent)
        if validation_check is not None:
            raise ValueError(validation_check)

        # create a new LogEvent object and spread the logevent data into it
        logevent = LogEvent(**log_data)

        # insert and commit the logevent to the DB
        cursor.execute('INSERT INTO logs (level, message, created_at, author_name) VALUES (?, ?, ?, ?)', (logevent.level, logevent.message, logevent.created_at, logevent.author_name,))
        con.commit()
        close_db(con)

        # print to console
        if is_system is True:
            print(f"📝[{level.name}|🤖{SYSAUTHOR}] ({human_timestamp}) | {message}")
        print(f"📝[{level.name}|🧑‍🚀{author_username}] ({human_timestamp}) | {message}")
        return
    except ValueError as e:
        close_db(con)
        print(f"🚨[{LogLevel.ERROR.name}|🤖{SYSAUTHOR}] ({human_timestamp}) | {str(e)}")
    except Exception as e:
        close_db(con)
        print(f"🚨[{LogLevel.ERROR.name}|🤖{SYSAUTHOR}] ({human_timestamp}) | {str(e)}")


    # def log_endpoint_hit(self, time):
    #     if self.is_endpoint:
    #         print(f"🎯[{self.mode.name}|{time}]{self.endpoint}")

    # def log_event(self):
    #     # getting level symbol
    #     if self.level is LogLevel.TEST and self.mode is LogMode.DEBUG:
    #         _symbol = "🐞"
    #     if self.mode is LogMode.DATABASE:
    #         _symbol = "💽"
    #     if self.level is LogLevel.INFO:
    #         _symbol = "🔵"
    #     if self.level is LogLevel.OK:
    #         _symbol = "🟢"
    #     if self.level is LogLevel.ERROR:
    #         _symbol = "🟡"
    #     if self.level is LogLevel.CRITICAL:
    #         _symbol = "🔴"

    #     # get time in human readable format
    #     _time = datetime.fromtimestamp(self.created_at)

    #     # log an endpoint being hit
    #     if self.mode is LogMode.INFO and self.is_endpoint is True:
    #         self.log_endpoint_hit(_time)

    #     # if debug, only log to server console
    #     if self.mode is LogMode.DEBUG:
    #         print(f"{_symbol}[{self.mode.name}|{_time}]:{self.message}")
    #         return

    #     # log to server console
    #     print(f"{_symbol}[{self.mode.name}|{_time}]:{self.message}")

    #     # log to database
    #     try:
    #         request.post("http://localhost:8080/logs", data=json.dumps(self.__dict__), content_type="application/json")

    #         # # return response
    #         # return response(status=res.status_code, body=res.text)

    #         return

    #     except Exception as e:
    #         return self.log_event(LogEvent(LogMode.POST, LogEndpoint.LOGS, LogLevel.ERROR, {str(e)}, int(time.time()), 0, "IDA", False))
