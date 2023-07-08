import json

import discord

from discord import app_commands
from discord.ext import commands

from views.button_one import ButtonViewOne


class MyCog(commands.Cog):
    def __init__(self,  bot):
        self.bot = bot

    @app_commands.command(name="webhook")
    @app_commands.describe(webhook="The webhook the modals will be sent to")
    @app_commands.checks.has_permissions(administrator=True)
    async def webhook_cmd(self, interaction: discord.Interaction, webhook: str):
        with open("data.json", "w") as f:
            json.dump({"webhook": webhook}, f, indent=4)
        await interaction.response.send_message(f"The webhook URL has been set to: {webhook}", ephemeral=True)
        await interaction.channel.send(
            embed=discord.Embed(
                title="Title",
                description="Description",
                colour=0x000000
            ),
            view=ButtonViewOne()
        )


async def setup(bot):
    await bot.add_cog(MyCog(bot))