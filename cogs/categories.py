import json

import discord
from discord.app_commands import Choice, checks, choices, command, describe, guilds
from discord.ext import commands

from classes.Category import Category
from constants import GUILD_ID, LOGGER, MOD_ROLE_ID, OWNER_ROLE_ID
from JuiceBot import JuiceBot
from utils import error_embed, s, success_embed


async def setup(bot: JuiceBot):
    await bot.add_cog(CategoriesCog(bot))


class CategoriesCog(commands.Cog):

    def __init__(self, bot: JuiceBot):
        self.bot = bot
        self.categories = self.load_categories()


    def load_categories(self) -> list[Category]:
        with open("data/categories.json", 'r') as file:
            content: dict = json.load(file)
        return [Category(data) for data in content.get("categories", [])]

    def save_categories(self):
        categories_json = { "categories": [category.to_json() for category in self.categories] }
        with open("data/categories.json", 'w') as file:
            json.dump(categories_json, file, indent=4)
        LOGGER.info("Categories saved.")

    def get_category(self, id: int | None) -> Category | None:
        for category in self.categories:
            if category.id == id:
                return category
        return None


    @command(name="create_category", description="Create an category for the current channel")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    @describe(name="The name of the category")
    @describe(faq="The FAQ of the category")
    async def create_category(self, interaction: discord.Interaction, name: str, faq: str = "FAQ not available yet"):
        category = self.get_category(interaction.channel_id)
        if category is not None:
            return await interaction.response.send_message(embed=error_embed("This channel is already linked to a category... Maybe you wanted to do /update_faq ?"), ephemeral=True)
        if len(faq) > 2000:
            return await interaction.response.send_message(embed=error_embed(f"The faq can't be longer than 2000 characters due to discord limitations.\nCharacters : {len(faq)}"), ephemeral=True)
        new_category = Category({ "name": name, "channel": interaction.channel_id, "faq": faq, "seeds": [] })
        self.categories.append(new_category)
        LOGGER.info(f"Category {name} added by {interaction.user}.")
        await interaction.response.send_message(embed=success_embed(title="Category created!", description=f"The category {name} for the current channel has been created successfully!"))
        self.save_categories()


    @command(name="delete_category", description="Delete the current channel's category")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    async def delete_category(self, interaction: discord.Interaction):
        category = self.get_category(interaction.channel_id)
        if category is None:
            return await interaction.response.send_message(embed=error_embed("This channel doesn't have an FAQ..."), ephemeral=True)
        old_category = category.to_json()
        old_category_name = old_category.get("name", "Nameless Category")
        self.categories.remove(category)
        self.save_categories()
        LOGGER.info(f"Category {old_category_name} deleted by {interaction.user}. JSON: {old_category}")
        await interaction.response.send_message(embed=success_embed(title="Category deleted!", description=f"The category {old_category_name} for the current channel has been successfully deleted!"))
        try:
            await interaction.user.send(embed=success_embed(title="Category deleted!", description=f"The category {old_category_name} for the channel <#{interaction.channel_id}> has been successfully deleted!\n\nCategory JSON:```json\n{old_category}```"))
        except discord.HTTPException:
            return



    @command(name="faq", description="Display the FAQ for the current channel")
    @guilds(GUILD_ID)
    async def faq(self, interaction: discord.Interaction):
        category = self.get_category(interaction.channel_id)
        if category is None:
            return await interaction.response.send_message(embed=error_embed("This channel isn't linked to a category..."))
        await interaction.response.send_message(embed=success_embed(title=category.name, description=category.faq))


    @command(name="edit_faq", description="Edit the FAQ of the current channel")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    @describe(text="The new FAQ")
    async def edit_faq(self, interaction: discord.Interaction, text: str):
        category = self.get_category(interaction.channel_id)
        if category is None:
            return await interaction.response.send_message(embed=error_embed("This channel isn't linked to a category... Maybe you wanted to do /new_category ?"), ephemeral=True)
        old_faq = category.faq
        category.edit_faq(text)
        self.save_categories()
        LOGGER.info(f"FAQ of {category.name} edited by {interaction.user}.")
        await interaction.response.send_message(embed=success_embed(title="FAQ updated!", description="The FAQ for the current channel has been successfully updated!"))
        try:
            await interaction.user.send(embed=success_embed(title="FAQ updated!", description=f"The FAQ for the channel <#{interaction.channel_id}> has been successfully updated!\n\nOld FAQ:```{old_faq}```"))
        except discord.HTTPException:
            return



    @command(name="seeds", description="Display the SSG Seeds used for the current channel's category")
    @guilds(GUILD_ID)
    async def seeds(self, interaction: discord.Interaction):
        category = self.get_category(interaction.channel_id)
        if category is None:
            return await interaction.response.send_message(embed=error_embed("This channel isn't linked to a category..."))
        embed = success_embed(title=category.name, description=f"{len(category.seeds)} seed{s(category.seeds)} found.")
        for seed in category.seeds:
            embed.add_field(name=f"{seed.name} ({seed.version})", value=f"`{seed.seed}`", inline=False)
        await interaction.response.send_message(embed=embed)


    @command(name="add_seed", description="Add a SSG Seed for the current channel's category")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    @describe(seed_name="The new seed's name")
    @describe(seed="The seed")
    @describe(seed_version="The version of Minecraft the seed should be played on")
    async def add_seed(self, interaction: discord.Interaction, seed_name: str, seed: str, seed_version: str):
        category = self.get_category(interaction.channel_id)
        if category is None:
            return await interaction.response.send_message(embed=error_embed("This channel is not linked to a category..."), ephemeral=True)
        if category.get_seed(seed) is not None:
            return await interaction.response.send_message(embed=error_embed("This seed already exist for this category... Maybe you wanted to do /edit_seed ?"), ephemeral=True)
        new_seed = { "name": seed_name, "seed": seed, "version": seed_version }
        category.add_seed(new_seed)
        category.sort_seeds()
        self.save_categories()
        LOGGER.info(f"Seed {seed} added to {category.name} by {interaction.user}.")
        await interaction.response.send_message(embed=success_embed(title="Seed added!", description=f"The seed {seed} was added successfully !"))


    @command(name="edit_seed", description="Edit a seed for the current channel's category")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    @describe(seed="The seed you want to edit")
    @describe(change="What you want to change")
    @choices(change=[
        Choice(name="seed", value="seed"),
        Choice(name="name", value="name"),
        Choice(name="version", value="version")
    ])
    @describe(new_value="The new value")
    async def edit_seed(self, interaction: discord.Interaction, seed: str, change: str, new_value: str):
        category = self.get_category(interaction.channel_id)
        if category is None:
            return await interaction.response.send_message(embed=error_embed("This channel is not linked to a category..."), ephemeral=True)
        if (current_seed := category.get_seed(seed)) is None:
            return await interaction.response.send_message(embed=error_embed("This seed is not used for this category..."), ephemeral=True)
        old_data = current_seed.to_json()
        new_data = current_seed.to_json()
        new_data[change] = new_value
        current_seed.edit_data(new_data)
        category.sort_seeds()
        self.save_categories()
        LOGGER.info(f"Seed {seed} for {category.name} edited by {interaction.user}. JSON: {old_data}")
        await interaction.response.send_message(embed=success_embed(title="Seed edited!", description=f"The seed {seed} was edited successfully !\n\nOld Seed JSON:```json\n{old_data}```"))


    @command(name="remove_seed", description="Remove a seed from the current channel's category")
    @guilds(GUILD_ID)
    @checks.has_any_role(MOD_ROLE_ID, OWNER_ROLE_ID)
    @describe(seed="The seed you want to remove")
    async def remove_seed(self, interaction: discord.Interaction, seed: str):
        category = self.get_category(interaction.channel_id)
        if category is None:
            return await interaction.response.send_message(embed=error_embed("This channel is not linked to a category..."), ephemeral=True)
        if (old_seed := category.get_seed(seed)) is None:
            return await interaction.response.send_message(embed=error_embed("This seed is not used for this category..."), ephemeral=True)
        category.remove_seed(seed)
        self.save_categories()
        LOGGER.info(f"Seed {seed} for {category.name} removed by {interaction.user}. JSON: {old_seed.to_json()}")
        await interaction.response.send_message(embed=success_embed(title="Seed deleted!", description=f"The seed {seed} was deleted succesfully !\n\nSeed JSON:```json\n{old_seed.to_json()}```"))
