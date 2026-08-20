from datetime import UTC, datetime
from logging import INFO, FileHandler, Formatter, LogRecord, StreamHandler, getLogger
from sys import stdout
from time import gmtime

from discord.utils import _ColourFormatter


class DailyFileHandler(FileHandler):
    def __init__(self, directory: str = "logs"):
        self._directory = directory
        self._current_date = datetime.now(UTC).date()
        super().__init__(f"{directory}/{self._current_date}.log")

    def emit(self, record: LogRecord):
        current_date = datetime.now(UTC).date()
        if current_date != self._current_date:
            self._current_date = current_date
            self.close()
            self.baseFilename = f"{self._directory}/{current_date}.log"
            self.stream = self._open()
        super().emit(record)


_stream_handler = StreamHandler(stdout)
_stream_handler.setFormatter(_ColourFormatter())

_file_handler_formatter = Formatter("%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_file_handler_formatter.converter = gmtime
_file_handler = DailyFileHandler(directory="logs")
_file_handler.setFormatter(_file_handler_formatter)

LOGGER = getLogger("JuiceBot")
LOGGER.addHandler(_stream_handler)
LOGGER.addHandler(_file_handler)
LOGGER.setLevel(INFO)
