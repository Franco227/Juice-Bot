from re import search

import discord
from aiohttp import ClientResponse, ClientSession
from discord.app_commands import checks, command, guilds
from discord.ext import commands

from constants import COLORS, GUILD_ID, MOD_ROLE_ID, OWNER_ROLE_ID
from JuiceBot import JuiceBot
from utils import dtime, error_embed, s


async def setup(bot: JuiceBot):
    await bot.add_cog(SRCCog(bot))


class SRCCog(commands.Cog):

    def __init__(self, bot: JuiceBot):
        self.bot = bot
        self.api = "https://www.speedrun.com/api/v1"
        self.game_id = "m1mnjexd"
        self.seed_regex = r"-?\d{14,}"


    async def get_list_data(self, response: ClientResponse) -> list[dict]:
        return (await response.json()).get("data") or []


    async def get_rsg_variables(self, session: ClientSession) -> dict[str, list[str]] | None:
        rsg_variables = {}

        async with session.get(f"{self.api}/games/{self.game_id}/variables") as response:
            if response.status != 200:
                return None
            data = await self.get_list_data(response)
        for variable in data:
            if variable.get("category") is None:
                continue
            values = variable.get("values", {}).get("values", {})
            rsg_values = [id for id, value in values.items() if "RSG" in value.get("label", "")]
            if rsg_values:
                rsg_variables[variable.get("id")] = rsg_values

        return rsg_variables


    def is_seed_valid(self, seed: int) -> bool:
        if not -2**63 <= seed < 2**63:
            return False
        multiplier = 0x5DEECE66D
        addend = 11
        inverse_multiplier = 0xDFE05BCB1365
        double_multiplier = 0xBB20B4600A69
        double_addend = 0x40942DE6BA
        state_modulus = 1 << 48
        basis_a_x, basis_a_y = 7847617, 4824621
        basis_b_x, basis_b_y = 18218081, -24667315

        seed %= 2**64
        high = seed >> 32
        low = seed % 2**32

        coordinate_a = (-basis_b_y * high + basis_b_x * low + 67552711) % 2**64 >> 32
        coordinate_b = (-basis_a_y * high + basis_a_x * low + basis_a_x + 2**63) % 2**64 - 2**63 >> 32
        second_state = basis_a_x * coordinate_a - basis_b_x * coordinate_b
        initial_state = (second_state - addend) * inverse_multiplier % state_modulus

        first_int = (multiplier * initial_state + addend) % state_modulus >> 16
        second_int = (((double_multiplier * initial_state + double_addend) % state_modulus >> 16) + 2**31) % 2**32 - 2**31
        return ((first_int << 32) + second_int) % 2**64 == seed


    @command(name="check_runs", description="Check pending runs for invalid seeds")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    async def check_runs(self, interaction: discord.Interaction):
        await interaction.response.send_message("Refreshing variables...")
        async with ClientSession() as session:
            rsg_variables = await self.get_rsg_variables(session)
            if rsg_variables is None:
                return await interaction.edit_original_response(content="", embed=error_embed("Failed to retrieve variables."))

            await interaction.edit_original_response(content="Retrieving runs...")
            query_params = '&'.join([
                f"game={self.game_id}",
                "status=new", # TODO: add command parameter for status param
                "orderby=submitted",
                "direction=asc",
                "max=200"
            ])
            async with session.get(f"{self.api}/runs?{query_params}") as response:
                if response.status != 200:
                    return await interaction.edit_original_response(content="", embed=error_embed("Failed to retrieve runs."))
                runs = await self.get_list_data(response)

        await interaction.edit_original_response(content="Scanning runs...")
        invalid_runs = {}
        scanned_runs = 0
        for run in runs:
            for variable, values in rsg_variables.items():
                if not run.get("values", {}).get(variable, "") in values:
                    continue
                scanned_runs += 1
                run_description = run.get("comment", "") or ""
                if not run_description:
                    break
                match = search(self.seed_regex, run_description)
                if not match:
                    continue
                if not self.is_seed_valid(int(match.group())):
                    invalid_runs[run.get("id")] = int(match.group())
                break
        description = f"{len(runs)} runs found, {scanned_runs} RSG runs scanned, {len(invalid_runs)} invalid seed{s(len(invalid_runs))} found.\n\n"
        embed = discord.Embed(
            title="Scan complete.",
            description=description + '\n'.join(f"Run [{run_id}](https://speedrun.com/mc_juice/runs/{run_id}) : {seed}" for run_id, seed in invalid_runs.items()),
            color=COLORS.green() if len(invalid_runs) == 0 else COLORS.red(),
            timestamp=dtime(),
        )
        await interaction.edit_original_response(content="", embed=embed)
