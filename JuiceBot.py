import asyncio, time
import disnake as discord
from disnake.ext import commands
from datetime import datetime

prefix = '/'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = commands.when_mentioned_or(prefix), help_command = None, intents = intents)

client_id = "976753770916630528"
permissions = 8
invite_link = f"https://discord.com/oauth2/authorize?client_id={client_id}&scope=bot&permissions={permissions}"
bot_version = "0.1"

admins = [507753823742459904]

def ping_color(latency):
    c = discord.Color
    colours = [red, c.red(), c.orange(), c.gold(), c.green(), green]
    values = [5000, 500, 350, 200, 100]
    for i, nbr in enumerate(values):
        if latency >= nbr: return colours[i]
    return green

def get_token():
    with open("TOKEN", 'r') as f:
        return f.read()

######################
##### BOT EVENTS #####
######################


@bot.event
async def on_ready():
    t = str(datetime.now())
    time = f"the {t[8:10]}/{t[5:7]}/{t[:4]} at {t[11:13]}h{t[14:16]}"
    print(f" Bot connected {time}")
    connected = discord.Embed(title = f"Bot connected {time} !", colour = discord.Colour.green())
    try: await bot.get_guild(log_guild).get_channel(log_channel).send(embed = connected)
    except: pass
    await bot.change_presence(activity = discord.Game(name = "MC JUIGE"))



######################
#### BOT COMMANDS ####
######################


@bot.slash_command(description = "Display the bot version")
async def version(inter):
    await inter.send(f"Version {bot_version}")


@bot.slash_command(description = "Display bot latency")
async def ping(inter):
    timePing = time.monotonic()
    await inter.send(":ping_pong: **Pong !**")
    botLatency = round(1000 * (time.monotonic() - timePing), 2)
    if botLatency >= 1000: seconds = f" (`{round(botLatency / 1000)}s`)"
    embed = discord.Embed(title = ":ping_pong: **Pong !**", description = f"**:robot: Bot Latency :** `{botLatency}ms`{seconds}", color = ping_colour(botLatency))
    await inter.edit_original_message(content = "", embed = embed)

@bot.slash_command(description = "Display the FAQ for the current channel")
async def faq(inter):
    await inter.send("This channel doesn't have an faq...")


bot.run(get_token())
