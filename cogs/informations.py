import discord
from discord.app_commands import command, guilds
from discord.ext import commands
from time import monotonic

from constants import BOT_VERSION, COLORS, GUILD_ID
from utils import default_embed

async def setup(bot: commands.Bot):
    await bot.add_cog(InformationsCog(bot))


class InformationsCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    def ping_color(self, latency: float):
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


    @command(name="version", description="Display the bot version")
    @guilds(GUILD_ID)
    async def version(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Version {BOT_VERSION}")


    @command(name="dif", description="Do it first")
    @guilds(GUILD_ID)
    async def dif(self, interaction: discord.Interaction):
        await interaction.response.send_message("Dear runner,\n\nDo it first.\n\n- The Mods")


    @command(name="ping", description="Display bot latency")
    @guilds(GUILD_ID)
    async def ping(self, interaction: discord.Interaction):
        time_start = monotonic()
        await interaction.response.send_message(":ping_pong: **Pong !**")
        latency = round(1000 * (monotonic() - time_start), 2)
        seconds = f" (`{round(latency / 1000)}s`)" if latency >= 1000 else ""
        embed = discord.Embed(title=":ping_pong: **Pong !**", description=f"**:robot: Bot Latency :** `{latency}ms`{seconds}", color=self.ping_color(latency))
        await interaction.edit_original_response(content="", embed=embed)


    @command(name="requirements", description="Display the requirements for a new category to be added")
    @guilds(GUILD_ID)
    async def requirements(self, interaction: discord.Interaction):
        embed = default_embed(title="Requirements for a category to be added")
        embed.add_field(name="1 - Suggest the category", value="Send the category in <#991278937101582486> with the category's name and goal", inline=False)
        embed.add_field(name="2 - Get upvotes and runs", value="Get at least one of the following:\n> - 30 upvotes and 1 RSG run\n> - 25 upvotes and 3 RSG runs\\*\n> - 20 upvotes and 5 RSG runs\\*\n\n\\* : Each RSG run must be performed by a different runner", inline=False)
        embed.add_field(name="3 - Fill the form", value="Fill [this form](https://forms.gle/UYyHiC2LdbGWw3S2A)", inline=False)
        embed.add_field(name="4 - Wait for a public poll", value="Mods will debate to see if the category is worth adding, and will then either make a poll or tell you no", inline=False)
        embed.add_field(name="5 - Get enough votes", value="If the category gets enough votes, it gets added", inline=False)
        await interaction.response.send_message(embed=embed)
