import discord
from discord.app_commands import command, describe, guilds, checks
from discord.ext import commands

from constants import GUILD_ID, OWNER_ROLE_ID
from utils import error_embed, get_random_status, success_embed


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))


class AdminCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @command(name="change_status", description="Change the bot's status")
    @guilds(GUILD_ID)
    @checks.has_role(OWNER_ROLE_ID)
    async def change_status(self, interaction: discord.Interaction):
        await self.bot.change_presence(activity = discord.Game(name=get_random_status()))
        await interaction.response.send_message("Done !", ephemeral=True)


    @command(name="dm", description="Dm a user")
    @guilds(GUILD_ID)
    @checks.has_role(OWNER_ROLE_ID)
    @describe(user="The user you want to send a message to")
    @describe(message="Your message, use \\n for new lines")
    async def dm(self, interaction: discord.Interaction, user: discord.Member, message: str):
        try:
            await user.send(message.replace('\\n', '\n'))
            await interaction.response.send_message(embed=success_embed(title="Message sent!", description=""), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(f"Couldn't send the message...\n`{e}`"), ephemeral=True)

    @command(name="send", description="Send a message")
    @guilds(GUILD_ID)
    @checks.has_role(OWNER_ROLE_ID)
    @describe(channel="The channel you want to send the message to")
    @describe(message="Your message, use \\n for new lines")
    async def send(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        try:
            await channel.send(message.replace('\\n', '\n'))
            await interaction.response.send_message(embed=success_embed(title="Message sent!", description=""), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(f"Couldn't send the message...\n`{e}`"), ephemeral=True)

    @command(name="clear_messages", description="Clear the last messages")
    @guilds(GUILD_ID)
    @checks.has_any_role(OWNER_ROLE_ID)
    @describe(messages="The amount of messages you want to delete")
    @describe(reason="The reason for deletion")
    async def clear_messages(self, interaction: discord.Interaction, messages: int, reason: str = ""):
        try:
            await interaction.response.send_message(embed=success_embed(title=f"Deleting {messages} messages...", description=f"Reason: {reason}" if reason else ""), ephemeral=True)
            await interaction.channel.purge(limit=messages, reason=reason)
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(f"Couldn't delete messages...\n`{e}`"), ephemeral=True)
