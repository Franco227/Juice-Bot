from discord import Intents, Color
from discord.utils import _ColourFormatter
from logging import getLogger, INFO, StreamHandler


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
MOD_ROLE_ID = 936168762078560266
OWNER_ROLE_ID = 963803874911735869
SUS_ROLE_ID = 1447310460004204694

# Bot Utils
CLIENT_ID = 976753770916630528
PERMISSIONS = 8
INVITE_LINK = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions={PERMISSIONS}"

# Logger
_logger_stream_handler = StreamHandler()
_logger_stream_handler.setFormatter(_ColourFormatter())
LOGGER = getLogger("JuiceBot")
LOGGER.addHandler(_logger_stream_handler)
LOGGER.setLevel(INFO)

# Other
COLORS = Color
