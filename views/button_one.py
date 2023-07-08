import discord
from discord import ui

from views.modal_one import MyModalOne


class ButtonViewOne(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="persistent:button_one")
    async def button_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MyModalOne())
