import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reload")
    async def reload(self, interaction: discord.Interaction, cog: str):
        if interaction.user.id not in self.bot.admins:
            return
        await self.bot.reload_extension(cog)
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Reloaded Cogs",
                description=cog,
            )
        )

    @reload.autocomplete(name="cog")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        options = [cog for cog in self.bot.extensions.keys()]
        return [
            app_commands.Choice(name=option, value=option)
            for option in options
            if current.lower() in option.lower()
        ]

    @commands.group(invoke_without_command=True)
    async def sync(
        self, ctx: commands.Context, guild_id: Optional[int], copy: bool = False
    ) -> None:
        if ctx.author.id not in self.bot.admins:
            return
        if guild_id:
            guild = discord.Object(id=guild_id)
        else:
            guild = ctx.guild

        if copy:
            self.bot.tree.copy_global_to(guild=guild)

        synced = await self.bot.tree.sync(guild=guild)
        for command in synced:
            print("[Command] {0:12} [ID] {1}".format(command.name, command.id))
        await ctx.send(f"Successfully synced {len(synced)} commands")

    @sync.command(name="global")
    async def sync_global(self, ctx: commands.Context):
        if ctx.author.id not in self.bot.admins:
            return
        synced = await self.bot.tree.sync(guild=None)
        await ctx.send(f"Successfully synced {len(synced)} commands")

    @sync.command(name="duplicate")
    async def sync_clear_duplicates(self, ctx: commands.Context):
        if ctx.author.id not in self.bot.admins:
            return
        for guild in self.bot.guilds:
            self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)
        await ctx.send(f"Successfully cleared duplicates")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
