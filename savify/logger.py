class Logger:
    def __init__(self, quiet=False):
        self.log = ''
        self.quiet = quiet

    def __print(self, tag: str, message: str):
        self.log += message + '\n'
        if not self.quiet:
            print(f'[{tag}] {message}')

    def log(self, message: str):
        self.__print('INFO', message)

    def warning(self, message: str):
        self.__print('WARN', message)

    def error(self, message: str):
        self.__print('ERROR', message)

    def debug(self, message: str):
        self.__print('DEBUG', message)
