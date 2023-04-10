from enum import Enum


class LogMode(Enum):
    DEBUG = 1
    DATABASE = 2
    FUNCTION = 3
    GET = 4
    POST = 5
    PUT = 6
    DELETE = 7


class LogEndpoint(Enum):
    LOGS = 1
    RECORDS = 2
    USERS = 3
    LOGIN = 4
    LOGOUT = 5
    HOME = 6
    RECORDSVIEW = 7
    USERSVIEW = 8
    LOGSVIEW = 9


# TEST log level is used for DEBUG outs and ENDPOINT hits (both used for debug/testing)
class LogLevel(Enum):
    INFO = 1
    OK = 2
    ERROR = 3
    CRITICAL = 4
    TEST = 5
