import discord
from discord.app_commands import command, describe, choices, guilds, Choice, Range
from discord.ext import commands
from scipy.stats import binom

from constants import GUILD_ID
from utils import default_embed, error_embed, s


async def setup(bot: commands.Bot):
    await bot.add_cog(OddsCog(bot))


class OddsCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.odds_list = [
            ("flint", 0.1, "Probability of obtaining {quantifier} {nb} flint{s_nb} from {trials} gravel{s_trials} mined", 1),
            ("ender_eye_breaks", 0.2, "Probability of {quantifier} {nb} eye break{s_nb} for {trials} eye throw{s_trials}", 1),
            ("seed", 0.125, "Probability of obtaining {quantifier} {nb} wheat seed{s_nb} from {trials} grass broken", 1)
        ]
        self.stats = [
            ("exactly", "=", binom.pmf),
            ("more than", ">", lambda nb, trials, p: 1 - binom.cdf(nb, trials, p)),
            ("less than", "<", lambda nb, trials, p: binom.cdf(nb, trials, p) - binom.pmf(nb, trials, p)),
            ("more or equal to", ">=", lambda nb, trials, p: 1 - binom.cdf(nb, trials, p) + binom.pmf(nb, trials, p)),
            ("less or equal to", "<=", binom.cdf)
        ]


    @command(name="odds", description="Check the probability of something idk")
    @guilds(GUILD_ID)
    @describe(of="What to check")
    @choices(of=[
        Choice(name="flint", value="flint"),
        Choice(name="ender_eye_breaks", value="ender_eye_breaks"),
        Choice(name="seed", value="seed")
    ])
    @describe(nb="The number expected")
    @describe(trials="The number of attempts")
    async def odds(self, interaction: discord.Interaction, of: str, nb: Range[int, 0], trials: Range[int, 1]):
        for odd_type, odd_p, odd_description, odd_factor in self.odds_list:
            if of == odd_type:
                description, p, factor = odd_description, odd_p, odd_factor
                break
        if nb * factor > trials:
            return await interaction.response.send_message(embed=error_embed("Wrong number or number of attempts"), ephemeral=True)
        description = description.format(nb=nb, trials=trials, s_nb=s(nb), s_trials=s(trials), quantifier="{quantifier}")
        embed = default_embed(title=f"Odds for {of}")
        for quantifier, operator, stat_func in self.stats:
            embed.add_field(name=description.format(quantifier=quantifier), value=f"`P(X {operator} {nb})` = `{round(100 * stat_func(nb, trials, p), 6)}%`", inline=False)
        await interaction.response.send_message(embed=embed)
