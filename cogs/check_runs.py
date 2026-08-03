from re import search

import discord
from aiohttp import ClientSession
from discord.app_commands import checks, command, guilds
from discord.ext import commands

from constants import COLORS, GUILD_ID, MOD_ROLE_ID, OWNER_ROLE_ID
from utils import dtime, s


async def setup(bot: commands.Bot):
    await bot.add_cog(CheckRunsCog(bot))


class CheckRunsCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.seed_regex = r"-?\d{14,}"
        self.base_url_start = "https://www.speedrun.com/api/v2/GetGameLeaderboard2?_r=eyJwYXJhbXMiOnsiZ2FtZUlkIjoibTFtbmpleGQiLCJjYXRlZ29yeUlkIjoi"
        self.base_url_end = "iLCJ2ZXJpZmllZCI6MCwib2Jzb2xldGUiOjF9fQ"
        self.request_data_list = [
            ("emQzcWo3OGs", "4lx75xrq"),  # Fishtank
            ("bWtleXhnOTI", "5q8w44yq"),  # CNI
            ("OWQ4bDU3cTI", "xqky9odl"),  # Break Beenest
            ("amRybncwbGs", "jqzzvp4q"),  # All Arthropods
            ("N2RneTczbGQ", "5q8w26rq"),  # All Buckets
            ("OWQ4bGxsbDI", "81wxmool"),  # All Deaths
            ("eGQxNXc2ODI", "013n28dq"),  # Half Death
            ("cmtsbjh4dzI", "810kw35q"),  # Saddle Master
            ("emRueWc0N2s", {"z19o7z81", "p12y324q", "81pm8x81", "xqky7zkl"}),  # Low%
            ("dmRveWpneTI", "rqv5jkw1"),  # Herobrine
            ("cTI1NWpxeTI", "jq68w93l"),  # Obtain Advancement
            ("cmtsMDA5bms", "gq7yyxyq"),  # Any% Superflat
            ("eGQxd3pvNDI", "9qj3zkol"),  # Quater
            ("emRubzVybjI", "mlnx63oq"),  # Mojang Banner
            ("emQzNWdtOGs", "zqo40dx1"),  # SMAC
            ("d2twcnEzajI", "p1277n4q"),  # All Nametags
            ("MDJxN2x3emQ", "21dmj0p1"),  # ACI
            ("N2tqNzh6eGs", "jqzm4zkl"),  # All Structures
            ("dmRvbjVveWs", "814n00jl"),  # Aether
            ("emQzbXZlbjI", "lx55xgr1"),  # WR
            ("d2RtcDdyM2Q", "139x86y1")  # All Sands
        ]


    def check_seed_validity(self, seed: int):
        seed = seed % 2**64
        a = 18218081
        b = 1 << 48
        c = 7847617
        d = ((((c * ((24667315 * (seed >> 32) + a * (seed % 2**32) + 67552711) % 2**64 >> 32) - a * (((-4824621 * (seed >> 32) + c * (seed % 2**32) + c) + 2**63) % 2**64 - 2**63 >> 32)) - 11) * 0xdfe05bcb1365) % b)
        return (((((0x5deece66d * d + 11) % b) >> 16) << 32) + (((((0xbb20b4600a69 * d + 0x40942de6ba) % b) >> 16) + 2**31) % 2**32 - 2**31)) % 2**64 == seed


    @command(name="check_runs", description="Check pending runs for invalid seed")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    async def check_runs(self, interaction: discord.Interaction):
        await interaction.response.send_message("Scanning for invalid seeds...")
        invalid_seeds = []
        runs_scanned = 0
        async with ClientSession() as session:
            for request_data in self.request_data_list:
                async with session.get(self.base_url_start + request_data[0] + self.base_url_end) as response:
                    if response.status == 200:
                        data = await response.json()
                    else: # TODO: find bypass
                        continue
                    runs_scanned += len(data.get("runList", []))
                    for run in data.get("runList", []):
                        run: dict
                        if "comment" not in run:
                            continue
                        if request_data[0] == "emRueWc0N2s":
                            if not any(value_id in request_data[1] for value_id in run.get("valueIds", [])):
                                continue
                        elif request_data[1] not in run.get("valueIds", []):
                            continue
                        match = search(self.seed_regex, run.get("comment", []))
                        if not match:
                            continue
                        description_seed = int(match.group())
                        if not self.check_seed_validity(description_seed):
                            invalid_seeds.append((run.get("id", "<invalid run id>"), description_seed))


        description = f"{runs_scanned} runs scanned,\n{len(invalid_seeds)} invalid seed{s(invalid_seeds)} found.\n"
        for run_id, seed in invalid_seeds:
            description += f"\n**Run [{run_id}](https://speedrun.com/mc_juice/runs/{run_id}) :** `{seed}`"

        embed = discord.Embed(
            title="Scan complete!",
            description=description,
            timestamp=dtime(),
            color=COLORS.green() if len(invalid_seeds) == 0 else COLORS.red()
        )
        await interaction.edit_original_response(content="", embed=embed)
