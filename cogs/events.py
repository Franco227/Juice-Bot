from asyncio import sleep as asleep
import time
import discord
from discord.ext import commands

from constants import BOT_VERSION, GUILD_ID, LOG_CHANNEL_ID, LOGGER, SUS_ROLE_ID
from utils import error_embed, get_random_status


async def setup(bot: commands.Bot):
    await bot.add_cog(EventsCog(bot))


class EventsCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reactions = [
            ("<:bedge:1072508860046250024>", "🛏️"),
            ("<:catsleep:1077225171569606748>", "🛏️"),
            ("<:bed:1117936940432490496>", "☀️"),
            ("🛏️", "<:bedge:1072508860046250024>")
        ]
        self.deleted_messages = []
        self.next_deleted_message_log_time = 0


    @commands.Cog.listener()
    async def on_ready(self):
        LOGGER.info(f"[v{BOT_VERSION}] Bot connected as {self.bot.user.name if self.bot.user else 'unknown bot'}.")
        while 1:
            await self.bot.change_presence(activity=discord.Game(name=get_random_status()))
            await asleep(600)


    async def delete_and_remove_access(self, message: discord.Message, source: str):
        message_content = f"Message: {message.content or 'None'}"
        filenames = f"Filenames: {', '.join(attachment.filename for attachment in message.attachments) if len(message.attachments) else 'None'}"
        LOGGER.warning(f"[{source}] Detected potential spam message from user {message.author}, deleting and removing the user's access. {message_content}; {filenames}")
        sus_role = message.guild.get_role(SUS_ROLE_ID)
        if sus_role:
            await message.author.add_roles(sus_role)
        await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            LOGGER.info(f"DM from {message.author}: {message.content}")
        if message.guild is None or message.guild.id != GUILD_ID:
            return

        # AutoReact
        for trigger, reaction in self.reactions:
            if message.content == trigger:
                await message.add_reaction(reaction)

        # Spambot prevention
        if len(message.attachments) == 4 and all(attachment.content_type == "image/jpeg" for attachment in message.attachments):
            await self.delete_and_remove_access(message, "4jpg")
            # if all(attachment.filename.startswith("IMG_") for attachment in message.attachments):
            #     await self.delete_and_remove_access(message, "IMG_")
            # if all(attachment.filename.split('.')[0] == str(i + 1) for i, attachment in enumerate(message.attachments)):
            #     await self.delete_and_remove_access(message, "1234")
        if message.content.count('|') >= 100:
            await self.delete_and_remove_access(message, "spoilers")
        if message.content.count("imgur") == 4:
            await self.delete_and_remove_access(message, "imgur")


    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        if messages[0].guild is None or messages[0].guild.id != GUILD_ID:
            return
        await self.send_multiple_deleted_messages_log(messages)


    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None or message.guild.id != GUILD_ID or message.channel.id == LOG_CHANNEL_ID or message.is_system():
            return
        current_timestamp = time.time()
        self.next_deleted_message_log_time = current_timestamp
        self.deleted_messages.append(message)
        await asleep(5)
        if self.next_deleted_message_log_time == current_timestamp:
            if len(self.deleted_messages) == 1:
                await self.send_deleted_message_log(self.deleted_messages[0])
            else:
                await self.send_multiple_deleted_messages_log(self.deleted_messages)
            self.deleted_messages = []


    async def send_deleted_message_log(self, message: discord.Message):
        embed = error_embed(title="Message deleted", description=message.content)
        embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar.url if message.author.avatar else None)
        if len(message.attachments) != 0:
            embed.add_field(name="Attachments", value=', '.join(attachment.filename for attachment in message.attachments), inline=False)
        embed.add_field(name="Channel", value=f"<#{message.channel.id}>")
        await self.bot.get_channel(LOG_CHANNEL_ID).send(embed=embed)

    async def send_multiple_deleted_messages_log(self, messages: list[discord.Message]):
        embed = error_embed(title="Messages deleted", description=f"{len(messages)} messages deleted.")
        embed.add_field(name="Channels", value=', '.join(channel.mention for channel in set(message.channel for message in messages)))
        if all(message.author.id == messages[0].author.id for message in messages[1:]):
            embed.set_author(name=f"{messages[0].author} ({messages[0].author.id})", icon_url=messages[0].author.avatar.url if messages[0].author.avatar else None)
        else:
            embed.add_field(name="Users", value=', '.join(author.mention for author in set(message.author for message in messages)), inline=False)
        await self.bot.get_channel(LOG_CHANNEL_ID).send(embed=embed)


    # TODO: add bot detection from reactions
