class LogLevel:
    SILENT = 0
    QUIET = 1
    WARN = 2
    DEBUG = 4


class Logger:
    def __init__(self, log_level=LogLevel.QUIET):
        self.log = ''
        self.log_level = log_level

    def __print(self, tag: str, message: str, log_level: int = LogLevel.SILENT):
        message = f'[{tag}]\t{message}'
        self.log += message + '\n'
        if log_level <= self.log_level:
            print(message)

    def info(self, message: str):
        self.__print('INFO', message, LogLevel.QUIET)

    def warning(self, message: str):
        self.__print('WARN', message, LogLevel.WARN)

    def error(self, message: str):
        self.__print('ERROR', message, LogLevel.QUIET)

    def debug(self, message: str):
        self.__print('DEBUG', message, LogLevel.DEBUG)
