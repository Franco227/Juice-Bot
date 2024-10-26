from datetime import datetime, UTC
from discord import Embed
from random import randrange

from constants import COLORS


def dtime() -> datetime:
    return datetime.now(UTC)

def get_random_status() -> str:
    with open("data/splash_texts.txt", 'r') as file:
        texts = file.readlines()
        return texts[randrange(len(texts))]

def s(list_or_count: list | int) -> str:
    if isinstance(list_or_count, list):
        return '' if len(list_or_count) == 1 else 's'
    if isinstance(list_or_count, int):
        return '' if list_or_count == 1 else 's'

def success_embed(description: str, title: str = "Success!", timestamp: datetime = None, *args) -> Embed:
    return Embed(title=title, description=description, color=COLORS.green(), timestamp=(timestamp or dtime()), *args)

def error_embed(description: str, title: str = "Error", timestamp: datetime = None, *args) -> Embed:
    return Embed(title=title, description=description, color=COLORS.red(), timestamp=(timestamp or dtime()), *args)

def default_embed(title: str, description: str = "", timestamp: datetime = None, *args) -> Embed:
    return Embed(title=title, description=description, color=COLORS.blue(), timestamp=(timestamp or dtime()), *args)