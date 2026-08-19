import discord
from discord.app_commands import checks, command, describe, guilds
from discord.ext import commands

from constants import GUILD_ID, LOG_CHANNEL_ID, LOGGER, OWNER_ROLE_ID
from utils import default_embed, error_embed, get_random_status, success_embed


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
            await interaction.response.send_message(embed=success_embed(title="Message sent!", description=f"Content: ```{message}```"), ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(embed=error_embed(title="Couldn't send message", description=f"```{e}```"), ephemeral=True)

    @command(name="send", description="Send a message")
    @guilds(GUILD_ID)
    @checks.has_role(OWNER_ROLE_ID)
    @describe(channel="The channel you want to send the message to")
    @describe(message="Your message, use \\n for new lines")
    async def send(self, interaction: discord.Interaction, channel: discord.TextChannel | discord.Thread, message: str):
        try:
            sent_message = await channel.send(message.replace('\\n', '\n'))
            await interaction.response.send_message(embed=success_embed(title="Message sent!", description=f"{sent_message.jump_url}"), ephemeral=True)
        except (discord.Forbidden, discord.HTTPException) as e:
            await interaction.response.send_message(embed=error_embed(title="Couldn't send message", description=f"```{e}```"), ephemeral=True)

    @command(name="clear_messages", description="Clear the last messages")
    @guilds(GUILD_ID)
    @checks.has_any_role(OWNER_ROLE_ID)
    @describe(messages="The amount of messages you want to delete")
    @describe(reason="The reason for deletion")
    async def clear_messages(self, interaction: discord.Interaction, messages: int, reason: str = ""):
        if type(interaction.channel) is not discord.TextChannel and type(interaction.channel) is not discord.Thread:
            return await interaction.response.send_message(embed=error_embed("Cannot clear messages in this type of channel."))
        try:
            await interaction.response.send_message(embed=default_embed(title=f"Deleting {messages} messages...", description=f"Reason: {reason}" if reason else ""), ephemeral=True)
            await interaction.channel.purge(limit=messages, reason=reason)
            LOGGER.info(f"{messages} purged in {interaction.channel.name} ({interaction.channel_id}) by {interaction.user.name} ({interaction.user.id}).")
            await interaction.edit_original_response(embed=success_embed(title=f"Deleted {messages} messages.", description=f"Reason: {reason}" if reason else ""))
            await self.bot.get_channel(LOG_CHANNEL_ID).send(embed=success_embed(title=f"{messages} purged", description=f"{messages} were purged in {interaction.channel.mention} by {interaction.user.mention}."))
        except (discord.Forbidden, discord.HTTPException) as e:
            await interaction.followup.send(embed=error_embed(title="Couldn't delete messages", description=f"```{e}```"))
