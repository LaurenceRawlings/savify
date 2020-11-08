class Logger(object):
    def __init__(self, quiet=False):
        self.log = ''
        self.quiet = quiet

    
    def log(self, msg):
        self.log += msg + '\n'
        if not self.quiet:
            print('[INFO] ' + msg)


    def warning(self, msg):
        self.log += msg + '\n'
        if not self.quiet:
            print('[WARN] ' + msg)


    def error(self, msg):
        self.log += msg + '\n'
        if not self.quiet:
            print('[ERROR] ' + msg)


    def debug(self, msg):
        self.log += msg + '\n'
        if not self.quiet:
            print('[DEBUG] ' + msg)
