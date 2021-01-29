import logging
import traceback
from .utils import create_dir
from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, log_location: str = '', log_level=logging.INFO):
        self.logger = logging.getLogger('savify')
        self.logger.setLevel(logging.DEBUG)

        time = (str(datetime.now()).replace(" ", "_")).replace(":", "_")
        log_location = f'{log_location}/logs/{time}_savify.log'
        formatter = logging.Formatter('[%(levelname)s]\t%(message)s')

        create_dir(Path(log_location).parent)

        if log_level is not None:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(log_level)
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_location)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_traceback(self):
        self.logger.error('An error occurred!')
        self.logger.error(traceback.format_exc())

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def info(self, message):
        self.logger.info(message)

