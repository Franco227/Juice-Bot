from datetime import datetime

import discord
from discord.app_commands import (
    Choice,
    Range,
    checks,
    choices,
    command,
    describe,
    guilds,
)
from discord.ext import commands

from constants import GUILD_ID, MOD_ROLE_ID, OWNER_ROLE_ID
from JuiceBot import JuiceBot
from utils import default_embed, error_embed, success_embed


async def setup(bot: JuiceBot):
    await bot.add_cog(PollCog(bot))


class PollCog(commands.Cog):

    def __init__(self, bot: JuiceBot):
        self.bot = bot
        self.number_reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


    @command(name="poll", description="Create a poll")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    @describe(channel="The channel you want to send the poll in")
    @describe(title="The title of the poll")
    @describe(description="The text of the poll")
    @describe(end_timestamp="The timestamp of when the poll ends")
    @describe(number_of_reactions="Number of reactions, leave empty for a yes/no poll")
    @describe(mention="The role you want to ping (default is Announcements)")
    @describe(attachment="The attachment of the poll")
    async def poll(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel,
            title: str,
            description: str,
            end_timestamp: int,
            number_of_reactions: Range[int, 2, 10] = 0,
            mention: discord.Role | None = None,
            attachment: discord.Attachment | None = None
        ):
        await interaction.response.send_message("Creating embed...")
        embed = default_embed(title=title, description=description.replace('\\n','\n'), timestamp=datetime.fromtimestamp(float(end_timestamp)))
        embed.set_footer(text = "Poll ends at")
        note = ""
        if attachment is not None:
            if attachment.content_type and attachment.content_type.startswith("image"):
                embed.set_image(url = attachment.url)
            else:
                note = "\nNote: The attachment could not be added to the poll."
        await interaction.edit_original_response(content="Sending poll...")
        try:
            message = await channel.send(content=mention.mention if mention else "", embed=embed)
        except (discord.Forbidden, discord.HTTPException) as e:
            return await interaction.edit_original_response(content="", embed=error_embed(f"The poll could not be sent !\n`{e}`"))
        await interaction.edit_original_response(content="Adding reactions...")
        if number_of_reactions == 0:
            await message.add_reaction("🟢")
            await message.add_reaction("🔴")
        else:
            for i in range(number_of_reactions):
                await message.add_reaction(self.number_reactions[i])
        await interaction.edit_original_response(content="", embed=success_embed(title="Poll sent out successfully!", description=f"https://discord.com/channels/{GUILD_ID}/{channel.id}/{message.id} \n{note}"))


    @command(name="edit_poll", description="Edit an existing poll")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    @describe(channel="The channel where the poll you want to edit is")
    @describe(message_id="The ID of the message of the poll")
    @describe(change="What you want to change")
    @choices(change=[
        Choice(name="title", value="title"),
        Choice(name="description", value="description"),
        Choice(name="timestamp", value="timestamp"),
        Choice(name="attachment", value="attachment")
    ])
    @describe(new_value="The new value (image link for attachment)")
    async def edit_poll(self, interaction: discord.Interaction, channel: discord.TextChannel, message_id: str, change: str, new_value: str):
        try:
            message_id = message_id.split('-')[1] if '-' in message_id else message_id
            message = await channel.fetch_message(int(message_id))
        except ValueError:
            return await interaction.response.send_message(embed=error_embed("Invalid message ID."), ephemeral=True)
        except (discord.Forbidden, discord.HTTPException) as e:
            return await interaction.response.send_message(embed=error_embed(f"Message not found.\n`{e}`"), ephemeral=True)
        if message.author != self.bot.user:
            return await interaction.response.send_message(embed=error_embed("This is not a poll."), ephemeral=True)
        embed = message.embeds[0]
        if change == "title":
            embed.title = new_value.format(title=embed.title)
        elif change == "description":
            embed.description = new_value.format(description=embed.description).replace('\\n','\n')
        elif change == "timestamp":
            try:
                timestamp = float(new_value)
            except ValueError:
                return await interaction.response.send_message(embed=error_embed("Invalid timestamp."), ephemeral=True)
            embed.timestamp = datetime.fromtimestamp(timestamp)
        elif change == "attachment":
            if not new_value.startswith("http"):
                return await interaction.response.send_message(embed=error_embed("Invalid attachment url."), ephemeral=True)
            embed.set_image(url=new_value)
        try:
            await message.edit(embed=embed)
        except (discord.Forbidden, discord.HTTPException) as e:
            return await interaction.response.send_message(embed=error_embed(f"An error occurred... Make sure that you input correct arguments.\n`{e}`"), ephemeral=True)
        await interaction.response.send_message(embed=success_embed(title="Poll edited successfully!", description=f"\n\nhttps://discord.com/channels/{GUILD_ID}/{channel.id}/{message.id}"))
