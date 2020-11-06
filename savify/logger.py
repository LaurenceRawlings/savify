class Logger(object):
    def __init__(self):
        self.final_destination = ''
        self.log = ''

    def warning(self, msg):
        self.log += msg + '\n'
        print('[WARN] ' + msg)

    def error(self, msg):
        self.log += msg + '\n'
        print('[ERROR] ' + msg)

    def debug(self, msg):
        self.log += msg + '\n'
        ffmpeg_destination = '[ffmpeg] Destination: '
        if ffmpeg_destination in msg:
            self.final_destination = msg.replace(ffmpeg_destination, '')
        return print('[INFO] ' + msg)
