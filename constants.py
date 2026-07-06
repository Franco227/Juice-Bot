from discord import Intents, Color
from discord.utils import _ColourFormatter
from logging import FileHandler, Formatter, getLogger, INFO, StreamHandler
from datetime import date
from sys import stdout


# Bot Data
BOT_PREFIX = '/'
BOT_INTENTS = Intents.all()
with open("data/TOKEN.txt", 'r') as file:
    BOT_TOKEN = file.read()
with open ("data/version.txt", 'r') as file:
    BOT_VERSION =  file.read()

# Ids
GUILD_ID = 936167959431364628
LOG_CHANNEL_ID = 1006553062464299109
HONEYPOT_CHANNEL_ID = 1521634880415596544
MOD_ROLE_ID = 936168762078560266
OWNER_ROLE_ID = 963803874911735869
SUS_ROLE_ID = 1447310460004204694

# Bot Utils
CLIENT_ID = 976753770916630528
PERMISSIONS = 8
INVITE_LINK = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions={PERMISSIONS}"

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
