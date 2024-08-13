import asyncio
import time
import json
import disnake as discord
from disnake.ext import commands
from datetime import datetime, UTC
from random import randrange
from scipy.stats import binom
from category import Category

BOT_PREFIX = '/'
CLIENT_ID = 976753770916630528
GUILD_ID = 936167959431364628
MOD_ROLE_ID = 936168762078560266
LOG_CHANNEL_ID = 1006553062464299109

intents = discord.Intents.all()
permissions = 8
invite_link = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions={permissions}"
bot = commands.Bot(command_prefix = commands.when_mentioned_or(BOT_PREFIX), help_command = None, intents = intents, test_guilds = [GUILD_ID])
with open ('version.txt', 'r') as file:
    BOT_VERSION = file.read()



######################
####### UTILS ########
######################


dInt = discord.OptionType.integer
dRole = discord.OptionType.role
dChan = discord.OptionType.channel
dAttach = discord.OptionType.attachment
dUser = discord.OptionType.user
colors = discord.Color

def dtime():
    return datetime.now(UTC)

def ping_color(latency):
    ping_colors = [
        (5000, 16711680),
        (750, colors.red()),
        (500, colors.orange()),
        (250, colors.gold()),
        (100, colors.green())
    ]
    for ping, color in ping_colors:
        if latency >= ping:
            return color
    return 65280

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

def load_categories():
    with open("categories.json", 'r') as file:
        categories = json.load(file).get("categories")
    return [Category(data) for data in categories]

categories = load_categories()

def save_categories():
    categories_json = { "categories": [cat.to_json() for cat in categories] }
    with open("categories.json", 'w') as file:
        json.dump(categories_json, file, indent = 4)
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
        return discord.Embed(title = "Error", description = "This channel isn't linked to a category...", color = colors.red())
    return discord.Embed(title = cat.name, description = cat.faq, color = colors.green())

def create_seeds_embed(id: int):
    cat = get_category(id)
    if cat is None:
        return discord.Embed(title = "Error", description = "This channel isn't linked to a category...", color = colors.red())
    embed = discord.Embed(title = cat.name, description = f"{len(cat.seeds)} seed{'s' if len(cat.seeds) > 1 else ''} found.", color = colors.green())
    for seed in cat.seeds:
        embed.add_field(name = f"{seed.name} ({seed.version})", value = f"`{seed.seed}`", inline = False)
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
        await bot.change_presence(activity = discord.Game(name = get_random_status()))
        await asyncio.sleep(600)


@bot.event
async def on_message(message):
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
async def on_message_delete(message):
    if message.guild is None or message.guild.id != GUILD_ID or message.channel.id == LOG_CHANNEL_ID or message.is_system():
        return
    msg = discord.Embed(title = "Message deleted", description = message.content, color = colors.red(), timestamp = dtime())
    try:
        msg.set_author(name = f"{message.author} ({message.author.id})", icon_url = message.author.avatar.url)
    except AttributeError:
        msg.set_author(name = f"{message.author} ({message.author.id})")
    msg.add_field(name = "Channel", value = f"<#{message.channel.id}>")
    await bot.get_channel(LOG_CHANNEL_ID).send(embed = msg)



######################
#### BOT COMMANDS ####
######################


@bot.slash_command(description = "Display the bot version")
async def version(inter):
    await inter.send(f"Version {BOT_VERSION}")



@bot.slash_command(description = "Change the bot's status")
async def change_status(inter):
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
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
    seconds = f" (`{round(latency / 1000)}s`)" if latency >= 1000 else ""
    embed = discord.Embed(title = ":ping_pong: **Pong !**", description = f"**:robot: Bot Latency :** `{latency}ms`{seconds}", color = ping_color(latency))
    await inter.edit_original_message(content = "", embed = embed)



@bot.slash_command(description = "Display the requirements for a new category to be added")
async def requirements(inter):
    embed = discord.Embed(title = "Requirements for a category to be added", description = "", timestamp = dtime())
    embed.add_field(name = "1 - Suggest the category", value = "Send the category in <#991278937101582486> with the category's name and goal", inline = False)
    embed.add_field(name = "2 - Get upvotes and runs", value = "Get at least one of the following:\n> - 30 upvotes and 1 RSG run\n> - 25 upvotes and 3 RSG runs\\*\n> - 20 upvotes and 5 RSG runs\\*\n\n\\* : Each RSG run must be performed by a different runner", inline = False)
    embed.add_field(name = "3 - Fill the form", value = "Fill [this form](https://forms.gle/UYyHiC2LdbGWw3S2A)", inline = False)
    embed.add_field(name = "4 - Wait for a public poll", value = "Mods will debate to see if the category is worth adding, and will then either make a poll or tell you no", inline = False)
    embed.add_field(name = "5 - Get enough votes", value = "If the category gets enough votes, it gets added", inline = False)
    await inter.send(embed = embed)



@bot.slash_command(description = "Create an category for the current channel", options = [
                    discord.Option(name = "name", description = "The name of the category", required = True),
                    discord.Option(name = "faq", description = "The FAQ of the category", required = False) ])
async def new_category(inter, name, faq = "FAQ not available yet"):
    cat = get_category(inter.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
    elif cat is not None:
        await inter.send("This channel is already linked to a category... Maybe you wanted to do /update_faq ?", ephemeral = True)
    elif len(faq) > 2000:
        await inter.send(f"The faq can't be longer than 2000 characters due to discord limitations.\nCharacters : {len(faq)}", ephemeral = True)
    else:
        new_cat = Category({ "name": name, "channel": inter.channel_id, "faq": faq, "seeds": [] })
        categories.append(new_cat)
        await inter.send("The category for the current channel has been created successfully!")
        print(f"Category {new_cat.name} added by {inter.author}.", end = "")
        save_categories()



@bot.slash_command(description = "Delete the current channel's category")
async def delete_category(inter):
    cat = get_category(inter.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
    elif cat is None:
        await inter.send("This channel doesn't have an FAQ...", ephemeral = True)
    else:
        old_cat = cat.to_json()
        categories.remove(cat)
        await inter.author.send(f"The category for the channel <#{inter.channel_id}> has been successfully deleted !\n\nCategory JSON:```json\n{old_cat}```")
        await inter.send("The category for the current channel has been successfully deleted !")
        print(f"Category {old_cat.get('name')} deleted by {inter.author}.", end = "")
        save_categories()



@bot.slash_command(description = "Display the FAQ for the current channel")
async def faq(inter):
    await inter.send(embed = create_faq_embed(inter.channel_id))



@bot.slash_command(description = "Edit the FAQ of the current channel",
                    options = [discord.Option(name = "text", description = "The new FAQ", required = True)])
async def edit_faq(inter, text):
    cat = get_category(inter.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
    elif cat is None:
        await inter.send("This channel isn't linked to a category... Maybe you wanted to do /new_category ?", ephemeral = True)
    else:
        old_faq = cat.faq
        cat.edit_faq(text)
        await inter.author.send(f"The FAQ for the channel <#{inter.channel_id}> got updated successfully !\n\nOld FAQ:```{old_faq}```")
        await inter.send("The FAQ for the current channel got updated successfully !")
        print(f"FAQ of {cat.name} edited by {inter.author}.", end = "")
        save_categories()



@bot.slash_command(description = "Display the SSG Seeds used for the current channel's category")
async def seeds(inter):
    await inter.send(embed = create_seeds_embed(inter.channel_id))



@bot.slash_command(description = "Add a SSG Seed for the current channel's category", options = [
                    discord.Option(name = "seed_name", description = "The new seed's name", required = True),
                    discord.Option(name = "seed", description = "The seed", required = True),
                    discord.Option(name = "seed_version", description = "The version of Minecraft the seed should be played on", required = True)
                    ])
async def add_seed(inter, seed_name, seed, seed_version):
    cat = get_category(inter.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
    elif cat is None:
        await inter.send("This channel is not linked to a category...", ephemeral = True)
    elif cat.get_seed(seed) is not None:
        await inter.send("This seed already exist for this category... Maybe you wanted to do /edit_seed ?", ephemeral = True)
    else:
        try:
            seed = int(seed)
        except ValueError:
            await inter.send("This seed is not valid.")
            return
        new_seed = { "name": seed_name, "seed": seed, "version": seed_version }
        cat.add_seed(new_seed)
        await inter.send(f"The seed {seed} was added successfully !")
        print(f"Seed {new_seed.get('seed')} added to {cat.name} by {inter.author}.", end = "")
        cat.sort_seeds()
        save_categories()



@bot.slash_command(description = "Edit a seed for the current channel's category", options = [
                    discord.Option(name = "seed", description = "The seed you want to edit", required = True),
                    discord.Option(name = "change", description = "What you want to change", required = True, choices = [
                        discord.OptionChoice(name = "seed", value = "seed"),
                        discord.OptionChoice(name = "name", value = "name"),
                        discord.OptionChoice(name = "version", value = "version") ]),
                    discord.Option(name = "new_value", description = "The new value", required = True) ])
async def edit_seed(inter, seed, change, new_value):
    cat = get_category(inter.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
    elif cat is None:
        await inter.send("This channel is not linked to a category...", ephemeral = True)
    elif (current_seed := cat.get_seed(seed)) is None:
        await inter.send("This seed is not used for this category...", ephemeral = True)
    else:
        old_seed = current_seed.to_json()
        if change == "seed":
            try:
                new_value = int(new_value)
            except ValueError:
                await inter.send("This seed is not valid.")
                return
            current_seed.edit_seed(new_value)
        elif change == "name":
            current_seed.edit_name(new_value)
        elif change == "version":
            current_seed.edit_version(new_value)
        await inter.send(f"The seed {seed} was edited successfully !\n\nOld Seed JSON:```json\n{old_seed}```")
        print(f"Seed {seed} for {cat.name} edited by {inter.author}.", end = "")
        cat.sort_seeds()
        save_categories()



@bot.slash_command(description = "Remove a seed from the current channel's category", options = [
                    discord.Option(name = "seed", description = "The seed you want to remove", required = True) ])
async def remove_seed(inter, seed):
    cat = get_category(inter.channel_id)
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
    elif cat is None:
        await inter.send("This channel is not linked to a category...", ephemeral = True)
    elif (old_seed := cat.get_seed(seed)) is None:
        await inter.send("This seed is not used for this category...", ephemeral = True)
    else:
        old_seed = old_seed.to_json()
        cat.remove_seed(seed)
        await inter.send(f"The seed {seed} was deleted succesfully !\n\nSeed JSON:```json\n{old_seed}```")
        print(f"Seed {seed} for {cat.name} removed by {inter.author}.", end = "")
        save_categories()




@bot.slash_command(description = "Check the probability of something idk", options = [
                    discord.Option(name = "of", description = "What to check", required = True, choices = [
                        discord.OptionChoice(name = "flint", value = "flint"),
                        discord.OptionChoice(name = "ender_eye_breaks", value = "ender_eye_breaks"),
                        discord.OptionChoice(name = "seed", value = "seed")
                    ]),
                    discord.Option(name = "nb", description = "The number expected", required = True,
                                    type = discord.OptionType.integer, min_value = 1),
                    discord.Option(name = "nb_trials", description = "The number of attempts", required = True,
                                    type = discord.OptionType.integer, min_value = 1) ])
async def odds(inter, of, nb, nb_trials):
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



@bot.slash_command(description = "Create a poll", options = [
                    discord.Option(name = "channel", description = "The channel you want to send the poll in", required = True, type = dChan),
                    discord.Option(name = "title", description = "The title of the poll", required = True),
                    discord.Option(name = "description", description = "The text of the poll", required = True),
                    discord.Option(name = "end_timestamp", description = "The timestamp of when the poll ends", required = True),
                    discord.Option(name = "number_of_reactions", description = "Number of reactions, leave empty for a yes/no poll", required = False,
                                    type = dInt, min_value = 2, max_value = 10),
                    discord.Option(name = "mention", description = "The role you want to ping (default is Announcements)", required = False, type = dRole),
                    discord.Option(name = "attachment", description = "The attachment of the poll", required = False, type = dAttach)
                    ])
async def poll(inter, channel, title, description, end_timestamp, number_of_reactions = 0, mention = None, attachment = None):
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
        return
    await inter.send("Creating embed...")
    poll_embed = discord.Embed(title = title, description = description.replace("\\n","\n"), timestamp = datetime.fromtimestamp(float(end_timestamp)))
    poll_embed.set_footer(text = "Poll ends at")
    note = ""
    if attachment is not None:
        if attachment.content_type.startswith("image"):
            poll_embed.set_image(url = attachment.url)
        else:
            note = "\nNote: The attachment could not be added to the poll."
    await inter.edit_original_message(content = "Sending poll...")
    try:
        message = await channel.send(content = mention.mention or "", embed = poll_embed)
    except Exception as e:
        await inter.edit_original_message(content = f":x: The poll could not be sent ! ({e})")
        return
    await inter.edit_original_message(content = "Adding reactions...")
    if (number_of_reactions == 0):
        await message.add_reaction("🟢")
        await message.add_reaction("🔴")
    else:
        for i in range(number_of_reactions):
            await message.add_reaction(reactions[i])
    await inter.edit_original_message(content = f"Poll sent out successfully !\n\n[Link to poll](https://discord.com/channels/{GUILD_ID}/{channel.id}/{message.id}){note}")



@bot.slash_command(description = "Edit an existing poll", options = [
                    discord.Option(name = "channel", description = "The channel where the poll you want to edit is", required = True, type = dChan),
                    discord.Option(name = "message_id", description = "The ID of the message of the poll", required = True),
                    discord.Option(name = "change", description = "What you want to change", required = True, choices = [
                        discord.OptionChoice(name = "title", value = "title"),
                        discord.OptionChoice(name = "description", value = "description"),
                        discord.OptionChoice(name = "timestamp", value = "timestamp"),
                        discord.OptionChoice(name = "attachment", value = "attachment")
                    ]),
                    discord.Option(name = "new_value", description = "The new value (image link for attachment)", required = True) ])
async def edit_poll(inter, channel, message_id, change, new_value):
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
        return
    try:
        message = await channel.fetch_message(message_id)
    except Exception as e:
        await inter.send(f"Message not found. ({e})", ephemeral = True)
        return
    if message.author != bot.user:
        await inter.send("This is not a poll.", ephemeral = True)
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
            await inter.send("Invalid timestamp.", ephemeral = True)
            return
        embed.timestamp = datetime.fromtimestamp(timestamp)
    elif change == "attachment":
        if not new_value.startswith("http"):
            await inter.send("Invalid attachment url.", ephemeral = True)
            return
        embed.set_image(url = new_value)
    try:
        await message.edit(embed = embed)
    except Exception as e:
        await inter.send(f"An error occurred... Make sure that you input correct arguments. ({e})", ephemeral = True)
        return
    await inter.send(f"Poll edited successfully!\n\n[Link to poll](https://discord.com/channels/{GUILD_ID}/{channel.id}/{message.id})")


@bot.slash_command(description = "Dm a user", options = [
                    discord.Option(name = "user", description = "The user you want to send a message to", required = True, type = dUser),
                    discord.Option(name = "message", description = "Your message, use \\n for new lines", required = True)
                    ])
async def dm(inter, user, message):
    if bot.get_guild(GUILD_ID).get_role(MOD_ROLE_ID) not in inter.author.roles:
        await inter.send("You do not have the permission to do that !", ephemeral = True)
        return
    try:
        await user.send(message.replace('\\n', '\n'))
        await inter.send("Message sent successfully!", ephemeral = True)
    except Exception as e:
        await inter.send(f"Couldn't send the message... ({e})", ephemeral = True)



bot.run(get_token())
