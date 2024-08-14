import asyncio
from aiohttp import ClientSession
from datetime import datetime, UTC
import discord
from discord.app_commands import describe, choices, Choice, Range
from discord.ext import commands
import json
from random import randrange
import re
from scipy.stats import binom
import time
from category import Category

BOT_PREFIX = '/'
CLIENT_ID = 976753770916630528
GUILD_ID = 936167959431364628
MOD_ROLE_ID = 936168762078560266
LOG_CHANNEL_ID = 1006553062464299109

INTENTS = discord.Intents.all()
PERMISSIONS = 8
INVITE_LINK = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions={PERMISSIONS}"
with open ('version.txt', 'r') as file:
    BOT_VERSION = file.read()

bot = commands.Bot(command_prefix=commands.when_mentioned_or(BOT_PREFIX), help_command=None, intents=INTENTS, test_guilds=[GUILD_ID])


######################
####### UTILS ########
######################

COLORS = discord.Color

def dtime():
    return datetime.now(UTC)

def ping_color(latency: int):
    ping_colors = [
        (5000, 16711680),
        (750, COLORS.red()),
        (500, COLORS.orange()),
        (250, COLORS.gold()),
        (100, COLORS.green())
    ]
    for ping, color in ping_colors:
        if latency >= ping:
            return color
    return 65280

def get_token():
    with open("TOKEN.txt", 'r') as f:
        return f.read()

def get_random_status():
    with open("splash_texts.txt", 'r') as f:
        texts = f.readlines()
        return texts[randrange(len(texts))]


######################
### SEED VALIDITY ####
######################

base_url_start = 'https://www.speedrun.com/api/v2/GetGameLeaderboard2?_r=eyJwYXJhbXMiOnsiZ2FtZUlkIjoibTFtbmpleGQiLCJjYXRlZ29yeUlkIjoi'
base_url_end = 'iLCJ2ZXJpZmllZCI6MH19'
request_data_list = [
    ('emQzcWo3OGs', '4lx75xrq'),  # Fishtank
    ('bWtleXhnOTI', '5q8w44yq'),  # CNI
    ('OWQ4bDU3cTI', 'xqky9odl'),  # Break Beenest
    ('amRybncwbGs', 'jqzzvp4q'),  # All Arthropods
    ('N2RneTczbGQ', '5q8w26rq'),  # All Buckets
    ('OWQ4bGxsbDI', '81wxmool'),  # All Deaths
    ('eGQxNXc2ODI', '013n28dq'),  # Half Death
    ('cmtsbjh4dzI', '810kw35q'),  # Saddle Master
    ('emRueWc0N2s', {'z19o7z81', 'p12y324q', '81pm8x81', 'xqky7zkl'}),  # Low%
    ('dmRveWpneTI', 'rqv5jkw1'),  # Herobrine
    ('cTI1NWpxeTI', 'jq68w93l'),  # Obtain Advancement
    ('cmtsMDA5bms', 'gq7yyxyq'),  # Any% Superflat
    ('eGQxd3pvNDI', '9qj3zkol'),  # Quater
    ('emRubzVybjI', 'mlnx63oq'),  # Mojang Banner
    ('emQzNWdtOGs', 'zqo40dx1'),  # SMAC
    ('d2twcnEzajI', 'p1277n4q'),  # All Nametags
    ('MDJxN2x3emQ', '21dmj0p1'),  # ACI
    ('N2tqNzh6eGs', 'jqzm4zkl'),  # All Structures
    ('dmRvbjVveWs', '814n00jl'),  # Aether
    ('emQzbXZlbjI', 'lx55xgr1'),  # WR
    ('d2RtcDdyM2Q', '139x86y1')  # All Sands
]

seed_regex = r'-?\d{14,}'

def check_seed_validity(seed: int):
    seed = seed % 2**64
    a = 18218081
    b = 1 << 48
    c = 7847617
    d = ((((c * ((24667315 * (seed >> 32) + a * (seed % 2**32) + 67552711) % 2**64 >> 32) - a * (((-4824621 * (seed >> 32) + c * (seed % 2**32) + c) + 2**63) % 2**64 - 2**63 >> 32)) - 11) * 0xdfe05bcb1365) % b)
    return (((((0x5deece66d * d + 11) % b) >> 16) << 32) + (((((0xbb20b4600a69 * d + 0x40942de6ba) % b) >> 16) + 2**31) % 2**32 - 2**31)) % 2**64 == seed


######################
##### CATEGORIES #####
######################

def load_categories():
    with open("categories.json", 'r') as file:
        categories = json.load(file).get("categories")
    return [Category(data) for data in categories]

categories = load_categories()

def save_categories():
    categories_json = { "categories": [cat.to_json() for cat in categories] }
    with open("categories.json", 'w') as file:
        json.dump(categories_json, file, indent=4)
        file.truncate()
    print(" Categories saved.")


def get_category(id: int):
    try:
        i = [cat.id for cat in categories].index(id)
    except ValueError:
        return None
    return categories[i]

def create_faq_embed(id: int):
    cat = get_category(id)
    if cat is None:
        return discord.Embed(title="Error", description="This channel isn't linked to a category...", color=COLORS.red())
    return discord.Embed(title=cat.name, description=cat.faq, color=COLORS.green())

def create_seeds_embed(id: int):
    cat = get_category(id)
    if cat is None:
        return discord.Embed(title="Error", description="This channel isn't linked to a category...", color=COLORS.red())
    embed = discord.Embed(title=cat.name, description=f"{len(cat.seeds)} seed{'s' if len(cat.seeds) > 1 else ''} found.", color=COLORS.green())
    for seed in cat.seeds:
        embed.add_field(name=f"{seed.name} ({seed.version})", value=f"`{seed.seed}`", inline=False)
    return embed


######################
##### BOT EVENTS #####
######################

@bot.event
async def on_ready():
    t = str(datetime.now())
    time = f"the {t[8:10]}/{t[5:7]}/{t[:4]} at {t[11:13]}h{t[14:16]}"
    print(f" Bot connected {time}")
    while 1:
        await bot.change_presence(activity=discord.Game(name=get_random_status()))
        await asyncio.sleep(600)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.guild is None:
        print(f"DM from {message.author}: {message.content}")
    if message.guild is None or message.guild.id != GUILD_ID:
        return

    # BEDGE
    if message.content in ["<:bedge:1072508860046250024>", "<:catsleep:1077225171569606748>"]:
        await message.add_reaction("🛏️")
    elif message.content == "<:bed:1117936940432490496>":
        await message.add_reaction("☀️")
    elif message.content == "🛏️":
        await message.add_reaction("<:bedge:1072508860046250024>")


@bot.event
async def on_message_delete(message: discord.Message):
    if message.guild is None or message.guild.id != GUILD_ID or message.channel.id == LOG_CHANNEL_ID or message.is_system():
        return
    embed = discord.Embed(title="Message deleted", description=message.content, color=COLORS.red(), timestamp=dtime())
    try:
        embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar.url)
    except AttributeError:
        embed.set_author(name=f"{message.author} ({message.author.id})")
    embed.add_field(name="Channel", value=f"<#{message.channel.id}>")
    await bot.get_channel(LOG_CHANNEL_ID).send(embed=embed)



######################
#### BOT COMMANDS ####
######################


@bot.tree.command(name="version", description="Display the bot version")
async def version(interaction: discord.Interaction):
    await interaction.response.send_message(f"Version {BOT_VERSION}")



@bot.tree.command(name="change_status", description="Change the bot's status")
async def change_status(interaction: discord.Interaction):
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
        return
    await bot.change_presence(activity = discord.Game(name=get_random_status()))
    await interaction.response.send_message("Done !", ephemeral=True)



@bot.tree.command(name="dif", description="Do it first")
async def dif(interaction: discord.Interaction):
    await interaction.response.send_message("Dear runner,\n\nDo it first.\n\n- The Mods")



@bot.tree.command(name="ping", description="Display bot latency")
async def ping(interaction: discord.Interaction):
    timePing = time.monotonic()
    await interaction.response.send_message(":ping_pong: **Pong !**")
    latency = round(1000 * (time.monotonic() - timePing), 2)
    seconds = f" (`{round(latency / 1000)}s`)" if latency >= 1000 else ""
    embed = discord.Embed(title=":ping_pong: **Pong !**", description=f"**:robot: Bot Latency :** `{latency}ms`{seconds}", color=ping_color(latency))
    await interaction.edit_original_response(content="", embed=embed)



@bot.tree.command(name="requirements", description="Display the requirements for a new category to be added")
async def requirements(interaction: discord.Interaction):
    embed = discord.Embed(title="Requirements for a category to be added", description="", timestamp=dtime())
    embed.add_field(name="1 - Suggest the category", value="Send the category in <#991278937101582486> with the category's name and goal", inline=False)
    embed.add_field(name="2 - Get upvotes and runs", value="Get at least one of the following:\n> - 30 upvotes and 1 RSG run\n> - 25 upvotes and 3 RSG runs\\*\n> - 20 upvotes and 5 RSG runs\\*\n\n\\* : Each RSG run must be performed by a different runner", inline=False)
    embed.add_field(name="3 - Fill the form", value="Fill [this form](https://forms.gle/UYyHiC2LdbGWw3S2A)", inline=False)
    embed.add_field(name="4 - Wait for a public poll", value="Mods will debate to see if the category is worth adding, and will then either make a poll or tell you no", inline=False)
    embed.add_field(name="5 - Get enough votes", value="If the category gets enough votes, it gets added", inline=False)
    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="new_category", description="Create an category for the current channel")
@describe(name="The name of the category")
@describe(faq="The FAQ of the category")
async def new_category(interaction: discord.Interaction, name: str, faq: str = "FAQ not available yet"):
    cat = get_category(interaction.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
    elif cat is not None:
        await interaction.response.send_message("This channel is already linked to a category... Maybe you wanted to do /update_faq ?", ephemeral=True)
    elif len(faq) > 2000:
        await interaction.response.send_message(f"The faq can't be longer than 2000 characters due to discord limitations.\nCharacters : {len(faq)}", ephemeral=True)
    else:
        new_cat = Category({ "name": name, "channel": interaction.channel_id, "faq": faq, "seeds": [] })
        categories.append(new_cat)
        await interaction.response.send_message("The category for the current channel has been created successfully!")
        print(f"Category {new_cat.name} added by {interaction.user}.", end="")
        save_categories()



@bot.tree.command(name="delete_category", description="Delete the current channel's category")
async def delete_category(interaction: discord.Interaction):
    cat = get_category(interaction.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
    elif cat is None:
        await interaction.response.send_message("This channel doesn't have an FAQ...", ephemeral=True)
    else:
        old_cat = cat.to_json()
        categories.remove(cat)
        await interaction.user.send(f"The category for the channel <#{interaction.channel_id}> has been successfully deleted !\n\nCategory JSON:```json\n{old_cat}```")
        await interaction.response.send_message("The category for the current channel has been successfully deleted !")
        print(f"Category {old_cat.get('name')} deleted by {interaction.user}.", end="")
        save_categories()



@bot.tree.command(name="faq", description="Display the FAQ for the current channel")
async def faq(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_faq_embed(interaction.channel_id))



@bot.tree.command(name="edit_faq", description="Edit the FAQ of the current channel")
@describe(text="The new FAQ")
async def edit_faq(interaction: discord.Interaction, text: str):
    cat = get_category(interaction.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
    elif cat is None:
        await interaction.response.send_message("This channel isn't linked to a category... Maybe you wanted to do /new_category ?", ephemeral=True)
    else:
        old_faq = cat.faq
        cat.edit_faq(text)
        await interaction.user.send(f"The FAQ for the channel <#{interaction.channel_id}> got updated successfully !\n\nOld FAQ:```{old_faq}```")
        await interaction.response.send_message("The FAQ for the current channel got updated successfully !")
        print(f"FAQ of {cat.name} edited by {interaction.user}.", end="")
        save_categories()



@bot.tree.command(name="seeds", description="Display the SSG Seeds used for the current channel's category")
async def seeds(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_seeds_embed(interaction.channel_id))



@bot.tree.command(name="add_seed", description="Add a SSG Seed for the current channel's category")
@describe(seed_name="The new seed's name")
@describe(seed="The seed")
@describe(seed_version="The version of Minecraft the seed should be played on")
async def add_seed(interaction: discord.Interaction, seed_name: str, seed: str, seed_version: str):
    cat = get_category(interaction.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
    elif cat is None:
        await interaction.response.send_message("This channel is not linked to a category...", ephemeral=True)
    elif cat.get_seed(seed) is not None:
        await interaction.response.send_message("This seed already exist for this category... Maybe you wanted to do /edit_seed ?", ephemeral=True)
    else:
        try:
            seed = int(seed)
        except ValueError:
            await interaction.response.send_message("This seed is not valid.")
            return
        new_seed = { "name": seed_name, "seed": seed, "version": seed_version }
        cat.add_seed(new_seed)
        await interaction.response.send_message(f"The seed {seed} was added successfully !")
        print(f"Seed {new_seed.get('seed')} added to {cat.name} by {interaction.user}.", end="")
        cat.sort_seeds()
        save_categories()



@bot.tree.command(name="edit_seed", description="Edit a seed for the current channel's category")
@describe(seed="The seed you want to edit")
@describe(change="What you want to change")
@choices(change=[
    Choice(name="seed", value="seed"),
    Choice(name="name", value="name"),
    Choice(name="version", value="version")
])
@describe(new_value="The new value")
async def edit_seed(interaction: discord.Interaction, seed: str, change: str, new_value: str):
    cat = get_category(interaction.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
    elif cat is None:
        await interaction.response.send_message("This channel is not linked to a category...", ephemeral=True)
    elif (current_seed := cat.get_seed(seed)) is None:
        await interaction.response.send_message("This seed is not used for this category...", ephemeral=True)
    else:
        old_seed = current_seed.to_json()
        if change == "seed":
            try:
                new_value = int(new_value)
            except ValueError:
                await interaction.response.send_message("This seed is not valid.")
                return
            current_seed.edit_seed(new_value)
        elif change == "name":
            current_seed.edit_name(new_value)
        elif change == "version":
            current_seed.edit_version(new_value)
        await interaction.response.send_message(f"The seed {seed} was edited successfully !\n\nOld Seed JSON:```json\n{old_seed}```")
        print(f"Seed {seed} for {cat.name} edited by {interaction.user}.", end="")
        cat.sort_seeds()
        save_categories()



@bot.tree.command(name="remove_seed", description="Remove a seed from the current channel's category")
@describe(seed="The seed you want to remove")
async def remove_seed(interaction: discord.Interaction, seed: str):
    cat = get_category(interaction.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
    elif cat is None:
        await interaction.response.send_message("This channel is not linked to a category...", ephemeral=True)
    elif (old_seed := cat.get_seed(seed)) is None:
        await interaction.response.send_message("This seed is not used for this category...", ephemeral=True)
    else:
        old_seed = old_seed.to_json()
        cat.remove_seed(seed)
        await interaction.response.send_message(f"The seed {seed} was deleted succesfully !\n\nSeed JSON:```json\n{old_seed}```")
        print(f"Seed {seed} for {cat.name} removed by {interaction.user}.", end="")
        save_categories()




@bot.tree.command(name="odds", description="Check the probability of something idk")
@describe(of="What to check")
@choices(of=[
    Choice(name="flint", value="flint"),
    Choice(name="ender_eye_breaks", value="ender_eye_breaks"),
    Choice(name="seed", value="seed")
])
@describe(nb="The number expected")
@describe(nb_trials="The number of attempts")
async def odds(interaction: discord.Interaction, of: str, nb: Range[int, 1], nb_trials: Range[int, 1]):
    if of == "flint":
        msg = f"Probability of obtaining :Q: {nb} flint(s) from {nb_trials} gravel(s) mined"
        p = 0.1
    elif of == "ender_eye_breaks":
        msg = f"Probability of :Q: {nb} eye break(s) for {nb_trials} eye throw(s)"
        p = 0.2
    elif of == "seed":
        msg = f"Probability of obtaining :Q: {nb} wheat seed(s) from {nb_trials} grass broken"
        p = 0.125
    else:
        await interaction.response.send_message("Error: Item not found", ephemeral=True)
        return
    p_e = round(binom.pmf(nb, nb_trials, p) * 100, 6)
    p_cie = round(binom.cdf(nb, nb_trials, p) * 100, 6)
    p_cse = round(100 - p_cie + p_e, 6)
    p_ci = round(p_cie - p_e, 6)
    p_cs = round(100 - p_cie, 6)
    embed = discord.Embed(title=f"Odds for {of}", timestamp=dtime())
    embed.add_field(name=msg.replace(":Q:", "exactly"), value=f"`P(X = {nb})` = `{p_e}%`", inline=False)
    embed.add_field(name=msg.replace(":Q:", "more than"), value=f"`P(X > {nb})` = `{p_cs}%`", inline=False)
    embed.add_field(name=msg.replace(":Q:", "less than"), value=f"`P(X < {nb})` = `{p_ci}%`", inline=False)
    embed.add_field(name=msg.replace(":Q:", "more or equal to"), value=f"`P(X >= {nb})` = `{p_cse}%`", inline=False)
    embed.add_field(name=msg.replace(":Q:", "less or equal to"), value=f"`P(X <= {nb})` = `{p_cie}%`", inline=False)
    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="poll", description="Create a poll")
@describe(channel="The channel you want to send the poll in")
@describe(title="The title of the poll")
@describe(description="The text of the poll")
@describe(end_timestamp="The timestamp of when the poll ends")
@describe(number_of_reactions="Number of reactions, leave empty for a yes/no poll")
@describe(mention="The role you want to ping (default is Announcements)")
@describe(attachment="The attachment of the poll")
async def poll(interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str, end_timestamp: int, number_of_reactions: Range[int, 2, 10] = 0, mention: discord.Role = None, attachment: discord.Attachment = None):
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
        return
    await interaction.response.send_message("Creating embed...")
    poll_embed = discord.Embed(title=title, description=description.replace("\\n","\n"), timestamp=datetime.fromtimestamp(float(end_timestamp)))
    poll_embed.set_footer(text = "Poll ends at")
    note = ""
    if attachment is not None:
        if attachment.content_type.startswith("image"):
            poll_embed.set_image(url = attachment.url)
        else:
            note = "\nNote: The attachment could not be added to the poll."
    await interaction.edit_original_response(content="Sending poll...")
    try:
        message = await channel.send(content=mention.mention or "", embed=poll_embed)
    except Exception as e:
        await interaction.edit_original_response(content=f":x: The poll could not be sent ! ({e})")
        return
    await interaction.edit_original_response(content="Adding reactions...")
    if (number_of_reactions == 0):
        await message.add_reaction("🟢")
        await message.add_reaction("🔴")
    else:
        for i in range(number_of_reactions):
            await message.add_reaction(reactions[i])
    await interaction.edit_original_response(content=f"Poll sent out successfully !\n\n[Link to poll](https://discord.com/channels/{GUILD_ID}/{channel.id}/{message.id}){note}")



@bot.tree.command(name="new_value", description="Edit an existing poll")
@describe(channel="The channel where the poll you want to edit is")
@describe(message_id="The ID of the message of the poll")
@describe(change="What you want to change")
@choices(change=[
    Choice(name="title", value="title"),
    Choice(name="description", value="description"),
    Choice(name="timestamp", value="timestamp"),
    Choice(name="attachment", value="attachment")
])
@describe(new_value="The new value (image link for attachment)")
async def edit_poll(interaction: discord.Interaction, channel: discord.TextChannel, message_id: int, change: str, new_value: str):
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
        return
    try:
        message = await channel.fetch_message(message_id)
    except Exception as e:
        await interaction.response.send_message(f"Message not found. ({e})", ephemeral=True)
        return
    if message.author != bot.user:
        await interaction.response.send_message("This is not a poll.", ephemeral=True)
        return
    embed = message.embeds[0]
    if change == "title":
        embed.title = new_value.replace("{title}", embed.title)
    elif change == "description":
        embed.description = new_value.replace("{description}", embed.description).replace("\\n","\n")
    elif change == "timestamp":
        try:
            timestamp = float(new_value)
        except ValueError:
            await interaction.response.send_message("Invalid timestamp.", ephemeral=True)
            return
        embed.timestamp = datetime.fromtimestamp(timestamp)
    elif change == "attachment":
        if not new_value.startswith("http"):
            await interaction.response.send_message("Invalid attachment url.", ephemeral=True)
            return
        embed.set_image(url = new_value)
    try:
        await message.edit(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred... Make sure that you input correct arguments. ({e})", ephemeral=True)
        return
    await interaction.response.send_message(f"Poll edited successfully!\n\n[Link to poll](https://discord.com/channels/{GUILD_ID}/{channel.id}/{message.id})")


@bot.tree.command(name="dm", description="Dm a user")
@describe(user="The user you want to send a message to")
@describe(message="Your message, use \\n for new lines")
async def dm(interaction: discord.Interaction, user: discord.Member, message: str):
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
        return
    try:
        await user.send(message.replace('\\n', '\n'))
        await interaction.response.send_message("Message sent successfully!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Couldn't send the message... ({e})", ephemeral=True)


@bot.tree.command(name="check_runs", description="Check pending runs for invalid seed")
async def check_runs(interaction: discord.Interaction):
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("You do not have the permission to do that !", ephemeral=True)
        return
    await interaction.response.send_message("Scanning for invalid seeds...")
    invalid_seeds = []
    runs_scanned = 0
    async with ClientSession() as session:
        for request_data in request_data_list:
            async with session.get(base_url_start + request_data[0] + base_url_end) as response:
                data = await response.json()
                for run in data['runList']:
                    runs_scanned += 1
                    if 'comment' not in run:
                        continue
                    if request_data[0] == 'emRueWc0N2s':
                        if not any(value_id in request_data[1] for value_id in run['valueIds']):
                            continue
                    elif request_data[1] not in run['valueIds']:
                        continue
                    match = re.search(seed_regex, run['comment'])
                    if not match:
                        continue
                    description_seed = int(match.group())
                    if not check_seed_validity(description_seed):
                        invalid_seeds.append((run["id"], description_seed))


    description = f"{runs_scanned} runs scanned,\n{len(invalid_seeds)} invalid seed(s) found.\n"
    for run_id, seed in invalid_seeds:
        description += f"\n**Run [{run_id}](https://speedrun.com/mc_juice/runs/{run_id}) :** `{seed}`"

    embed = discord.Embed(
        title="Scan complete!",
        description=description,
        timestamp=dtime(),
        color=COLORS.green() if len(invalid_seeds) == 0 else COLORS.red()
    )
    await interaction.edit_original_response(content="", embed=embed)


bot.run(get_token())
