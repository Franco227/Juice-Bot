from asyncio import sleep as asleep
import discord
from discord.ext import commands

from constants import BOT_VERSION, GUILD_ID, LOG_CHANNEL_ID, LOGGER
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


    @commands.Cog.listener()
    async def on_ready(self):
        LOGGER.info(f"[v{BOT_VERSION}] Bot connected as {self.bot.user.name if self.bot.user else 'unknown bot'}.")
        while 1:
            await self.bot.change_presence(activity=discord.Game(name=get_random_status()))
            await asleep(600)


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


    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None or message.guild.id != GUILD_ID or message.channel.id == LOG_CHANNEL_ID or message.is_system():
            return
        embed = error_embed(title="Message deleted", description=message.content)
        embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar.url if message.author.avatar else None)
        embed.add_field(name="Channel", value=f"<#{message.channel.id}>")
        await self.bot.get_channel(LOG_CHANNEL_ID).send(embed=embed)
