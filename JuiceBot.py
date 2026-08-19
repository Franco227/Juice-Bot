import discord
from aiohttp.client_exceptions import ClientConnectorError
from discord.app_commands import AppCommandError, errors
from discord.ext import commands

from constants import (
    BOT_INTENTS,
    BOT_PREFIX,
    BOT_TOKEN,
    GUILD_ID,
    LOG_CHANNEL_ID,
    LOGGER,
)
from utils import error_embed


class JuiceBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=BOT_PREFIX, intents=BOT_INTENTS, help_command=None)
        self.initial_extensions = [
            "cogs.admin",
            "cogs.categories",
            "cogs.check_runs",
            "cogs.events",
            "cogs.informations",
            "cogs.odds",
            "cogs.poll"
        ]

    async def setup_hook(self):
        LOGGER.info("Loading cogs...")
        for extension in self.initial_extensions:
            await self.load_extension(extension)
            LOGGER.info(f"Loaded {extension}")
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        LOGGER.info("Command tree synced.")

    async def send_log(self, embed: discord.Embed):
        log_channel = self.get_channel(LOG_CHANNEL_ID)
        if type(log_channel) is not discord.TextChannel:
            LOGGER.error("LOG_CHANNEL_ID is not pointing to a TextChannel.")
        else:
            await log_channel.send(embed=embed)


if __name__ == "__main__":
    bot = JuiceBot()

    @bot.tree.error
    async def on_tree_error(interaction: discord.Interaction, error: AppCommandError):
        if isinstance(error, (errors.MissingRole, errors.MissingAnyRole)):
            LOGGER.error(f"[MissingRoleException] User {interaction.user} ({interaction.user.id}) attempted command {interaction.command.name if interaction.command else 'unknown command'}.")
            return await interaction.response.send_message(embed=error_embed("You do not have the required permissions for this command."), ephemeral=True)
        if (command := interaction.command) is not None:
            if command._has_any_error_handlers():
                return
            LOGGER.error(f"Ignoring exception in command {command.name}", exc_info=error)
        else:
            LOGGER.error("Ignoring exception in command tree", exc_info=error)

    try:
        bot.run(BOT_TOKEN, reconnect=True)
    except ClientConnectorError:
        LOGGER.error("ClientConnectorError: no connection.")
