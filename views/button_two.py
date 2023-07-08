import discord
from discord import ui

from views.modal_two import MyModalTwo


class ButtonViewTwo(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅Code", style=discord.ButtonStyle.green, custom_id="persistent:button_two")
    async def button_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MyModalTwo())
