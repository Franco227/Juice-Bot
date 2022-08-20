import asyncio, time, json
import disnake as discord
from disnake.ext import commands
from datetime import datetime
from random import randrange
from scipy.stats import binom

prefix = '/'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = commands.when_mentioned_or(prefix), help_command = None, intents = intents, test_guilds = [936167959431364628])

client_id = "976753770916630528"
permissions = 8
invite_link = f"https://discord.com/oauth2/authorize?client_id={client_id}&scope=bot&permissions={permissions}"
bot_version = "0.12"



######################
####### UTILS ########
######################


dInt = discord.OptionType.integer
colors = discord.Color

def dtime():
    return datetime.utcnow()

def ping_color(latency):
    c = [16711680, colors.red(), colors.orange(), colors.gold(), colors.green(), 65280]
    values = [5000, 750, 500, 250, 100]
    for i, nbr in enumerate(values):
        if latency >= nbr: return c[i]
    return green

def get_token():
    with open("TOKEN", 'r') as f:
        return f.read()

def get_random_status():
    with open("splash_texts.txt", 'r') as f:
        texts = f.readlines()
        return texts[randrange(len(texts))]



######################
##### CATEGORIES #####
######################


def categories():
    with open("categories.json", 'r') as cats:
        return json.load(cats).get("categories")

def channels():
    return [cat.get("channel") for cat in categories()]

def get_cat(channel):
    for cat in categories():
        if cat.get("channel") == channel:
            return cat
    return None

def get_faq(channel):
    if channel not in channels():
        return "This channel doesn't have an FAQ..."
    return get_cat(channel).get("faq").replace("\\n", "\n")

def get_faq_embed(channel):
    if channel not in channels():
        return discord.Embed(title = "Unknown Category", description = "This channel doesn't have an FAQ...", color = colors.red())
    cat = get_cat(channel)
    return discord.Embed(title = cat.get("name"), description = cat.get("faq").replace("\\n", "\n"), color = colors.green())

def get_cat_index(cat):
    return categories().index(cat)



######################
##### BOT EVENTS #####
######################


@bot.event
async def on_ready():
    t = str(datetime.now())
    time = f"the {t[8:10]}/{t[5:7]}/{t[:4]} at {t[11:13]}h{t[14:16]}"
    print(f" Bot connected {time}")
    connected = discord.Embed(title = f"Bot connected {time} !", color = colors.green())
    try: await bot.get_guild(log_guild).get_channel(log_channel).send(embed = connected)
    except: pass
    while 1:
        await bot.change_presence(activity = discord.Game(name = get_random_status()))
        await asyncio.sleep(600)


@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.guild.id != 936167959431364628: return
    msg = message.content.split(' ')
    if "virst" in msg or "virt" in msg: await message.reply("crimson*")


@bot.event
async def on_message_delete(message):
    if message.guild.id != 936167959431364628 or message.channel.id == 1006553062464299109: return
    msg = discord.Embed(title = f"Message deleted", description = message.content, color = colors.red(), timestamp = dtime())
    msg.set_author(name = f"{message.author} ({message.author.id})", icon_url = message.author.avatar.url)
    msg.add_field(name = "Channel", value = f"<#{message.channel.id}>")
    await bot.get_channel(1006553062464299109).send(embed = msg)



######################
#### BOT COMMANDS ####
######################


@bot.slash_command(description = "Display the bot version")
async def version(inter):
    await inter.send(f"Version {bot_version}")



@bot.slash_command(description = "Change the bot's status")
async def change_status(inter):
    if bot.get_guild(936167959431364628).get_role(936168762078560266) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
        return
    await bot.change_presence(activity = discord.Game(name = get_random_status()))
    await inter.send("Done !", ephemeral = True)



@bot.slash_command(description = "Do it first")
async def dif(inter):
    await inter.send("Dear runner,\n\nDo it first.\n\n- The Mods")




@bot.slash_command(description = "Display bot latency")
async def ping(inter):
    timePing = time.monotonic()
    await inter.send(":ping_pong: **Pong !**")
    latency = round(1000 * (time.monotonic() - timePing), 2)
    if latency >= 1000: seconds = f" (`{round(latency / 1000)}s`)"
    else: seconds = ""
    embed = discord.Embed(title = ":ping_pong: **Pong !**", description = f"**:robot: Bot Latency :** `{latency}ms`{seconds}", color = ping_color(latency))
    await inter.edit_original_message(content = "", embed = embed)



@bot.slash_command(description = "Display the FAQ for the current channel")
async def faq(inter):
    await inter.send(embed = get_faq_embed(inter.channel_id))



@bot.slash_command(description = "Update the FAQ of the current channel",
                    options = [discord.Option(name = "text", description = "The new FAQ", required = True)])
async def update_faq(inter, text):
    if bot.get_guild(936167959431364628).get_role(936168762078560266) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
        return
    if inter.channel_id not in channels():
        await inter.send("This channel doesn't have an FAQ... Maybe you wanted to do /new_faq ?", ephemeral = True)
        return
    with open("categories.json", 'r') as cts:
        cats = json.load(cts)
        faq = get_cat(inter.channel_id).get("faq")
        cats.get("categories")[get_cat_index(get_cat(inter.channel_id))]["faq"] = text
    with open("categories.json", 'w') as cts:
        json.dump(cats, cts, indent = 4)
        cts.truncate()
    await inter.author.send(f"The FAQ for the channel <#{inter.channel_id}> got updated successfully !\n\nOld FAQ:```{faq}```New FAQ:```{text}```")
    await inter.send("The FAQ for the current channel got updated successfully !")



@bot.slash_command(description = "Create an FAQ for the current channel", options = [
                    discord.Option(name = "name", description = "The name of the category", required = True),
                    discord.Option(name = "text", description = "The new FAQ", required = True) ])
async def new_faq(inter, name, text):
    if bot.get_guild(936167959431364628).get_role(936168762078560266) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
        return
    if inter.channel_id in channels():
        await inter.send("This channel already has an FAQ... Maybe you wanted to do /update_faq ?", ephemeral = True)
        return
    if len(text) > 2000:
        await inter.send(f"The faq can't be longer than 2000 characters due to discord limitations.\nCharacters : {len(text)}", ephemeral = True)
        return
    with open("categories.json", 'r') as cts:
        cats = json.load(cts)
        new_cat = { "name": name, "channel": inter.channel_id, "faq": text }
        cats.get("categories").append(new_cat)
    with open("categories.json", 'w') as cts:
        json.dump(cats, cts, indent = 4)
        cts.truncate()
    await inter.author.send(f"The FAQ for the channel <#{inter.channel_id}> has been set successfully!\n\nFAQ:```{text}```")
    await inter.send("The FAQ for the current channel has been set successfully!")



@bot.slash_command(description = "Delete the current channel's FAQ")
async def delete_faq(inter):
    if bot.get_guild(936167959431364628).get_role(936168762078560266) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
        return
    if inter.channel_id not in channels():
        await inter.send("This channel doesn't have an FAQ...", ephemeral = True)
        return
    if len(text) > 2000:
        await inter.send(f"The faq can't be longer than 2000 characters due to discord limitations.\nCharacters : {len(text)}", ephemeral = True)
        return
    with open("categories.json", 'r') as cts:
        cats = json.load(cts)
        old_cat = get_cat(inter.channel_id)
        cats.get("categories").remove(old_cat)
    with open("categories.json", 'w') as cts:
        json.dump(cats, cts, indent = 4)
        cts.truncate()
    await inter.author.send(f"The FAQ for the channel <#{inter.channel_id}> has been successfully deleted !\n\nOld FAQ:```{old_cat.get('faq')}```")
    await inter.send("The FAQ for the current channel has been successfully deleted !")



@bot.slash_command(description = "Check the probability of something idk", options = [
                    discord.Option(name = "of", description = "What to check", required = True, choices = [
                        discord.OptionChoice(name = "flint", value = "flint"),
                        discord.OptionChoice(name = "ender_eye_breaks", value = "ender_eye_breaks")
                    ]),
                    discord.Option(name = "nb", description = "The number expected", required = True,
                                    type = discord.OptionType.integer, min_value = 1),
                    discord.Option(name = "nb_trials", description = "The number of attempts", required = True,
                                    type = discord.OptionType.integer, min_value = 1) ])
async def odds(inter, of, nb, nb_trials):
    if of == "flint":
        msg = f"Probability of obtaining :Q: {nb} flint(s) from {nb_trials} gravel(s) mined"
        p = 0.1
    if of == "ender_eye_breaks":
        msg = f"Probability of :Q: {nb} eye break(s) for {nb_trials} eye throw(s)"
        p = 0.2
    else:
        await inter.send("Error: Item not found", ephemeral = True)
        return
    p_e = round(binom.pmf(nb, nb_trials, p) * 100, 6)
    p_cie = round(binom.cdf(nb, nb_trials, p) * 100, 6)
    p_cse = round(100 - p_cie + p_e, 6)
    p_ci = round(p_cie - p_e, 6)
    p_cs = round(100 - p_cie, 6)
    embed = discord.Embed(title = f"Odds for {of}", timestamp = dtime())
    embed.add_field(name = msg.replace(":Q:", "exactly"), value = f"`P(X = {nb})` = `{p_e}%`", inline = False)
    embed.add_field(name = msg.replace(":Q:", "more than"), value = f"`P(X > {nb})` = `{p_cs}%`", inline = False)
    embed.add_field(name = msg.replace(":Q:", "less than"), value = f"`P(X < {nb})` = `{p_ci}%`", inline = False)
    embed.add_field(name = msg.replace(":Q:", "more or equal to"), value = f"`P(X >= {nb})` = `{p_cse}%`", inline = False)
    embed.add_field(name = msg.replace(":Q:", "less or equal to"), value = f"`P(X <= {nb})` = `{p_cie}%`", inline = False)
    await inter.send(embed = embed)



@bot.slash_command(description = "Add reactions under a poll", options = [
                    discord.Option(name = "channel_id", description = "The ID of the channel of the poll", required = True),
                    discord.Option(name = "message_id", description = "The ID of the message of the poll", required = True),
                    discord.Option(name = "number_of_reactions", description = "Number of reaction, leave empty for a yes/no poll", required = False,
                                    type = dInt, min_value = 2, max_value = 10) ])
async def poll(inter, channel_id, message_id, number_of_reactions = 0):
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    if bot.get_guild(936167959431364628).get_role(936168762078560266) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
        return
    channel = bot.get_channel(int(channel_id))
    if (channel is None):
        await inter.send("The channel_id is invalid !", ephemeral = True)
        return
    try: message = await channel.fetch_message(int(message_id))
    except discord.NotFound:
        await inter.send("The message_id is invalid !", ephemeral = True)
        return
    await inter.send("Adding reactions...")
    if (number_of_reactions == 0):
        await message.add_reaction("🟢")
        await message.add_reaction("🔴")
    else:
        for i in range(number_of_reactions): await message.add_reaction(reactions[i])
    await inter.edit_original_message(content = "All reactions were added !")


bot.run(get_token())
