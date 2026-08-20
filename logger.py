from datetime import UTC, datetime
from logging import INFO, FileHandler, Formatter, LogRecord, StreamHandler, getLogger
from sys import stdout

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


_logger_stream_handler = StreamHandler(stdout)
_logger_stream_handler.setFormatter(_ColourFormatter())
_logger_file_handler = DailyFileHandler(directory="logs")
_logger_file_handler.setFormatter(Formatter("%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

LOGGER = getLogger("JuiceBot")
LOGGER.addHandler(_logger_stream_handler)
LOGGER.addHandler(_logger_file_handler)
LOGGER.setLevel(INFO)
