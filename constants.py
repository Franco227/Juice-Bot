from datetime import date
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from os import environ
from sys import stdout

from discord import Color, Intents
from discord.utils import _ColourFormatter
from dotenv import load_dotenv

load_dotenv()

def _env(name: str) -> str:
    value = environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# Bot Data
BOT_PREFIX = _env("BOT_PREFIX")
BOT_INTENTS = Intents.all()
BOT_TOKEN = _env("BOT_TOKEN")
with open ("data/version.txt", 'r') as file:
    BOT_VERSION = file.read().strip()

# Ids
GUILD_ID = int(_env("GUILD_ID"))
LOG_CHANNEL_ID = int(_env("LOG_CHANNEL_ID"))
HONEYPOT_CHANNEL_ID = int(_env("HONEYPOT_CHANNEL_ID"))
MOD_ROLE_ID = int(_env("MOD_ROLE_ID"))
OWNER_ROLE_ID = int(_env("OWNER_ROLE_ID"))
SUS_ROLE_ID = int(_env("SUS_ROLE_ID"))

# Logger
_logger_stream_handler = StreamHandler(stdout)
_logger_stream_handler.setFormatter(_ColourFormatter())
_logger_file_handler = FileHandler(filename=f"logs/{date.today()}.log")
_logger_file_handler.setFormatter(Formatter("%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
LOGGER = getLogger("JuiceBot")
LOGGER.addHandler(_logger_stream_handler)
LOGGER.addHandler(_logger_file_handler)
LOGGER.setLevel(INFO)

# Other
COLORS = Color
