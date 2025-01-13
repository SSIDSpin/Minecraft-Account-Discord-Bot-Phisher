import discord
from discord import ui

from views.modal_two import MyModalTwo


class ButtonViewThree(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📙 How to?", style=discord.ButtonStyle.red, custom_id="persistent:button_two")
    async def button_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="How To Add A Security Email",
                description="""
                **Step 1:** Go To your [Microsoft Account](https://login.live.com/)
                **Step 2:** Click On "Security"
                **Step 3:** Click On Advanced Security Options"
                **Step 4:** Click "Add a new way to verify"
                **Step 5:** Click "Email a code"
                **Step 6:** Enter your email
                **Step 7:** Wait 1-2 minutes and retry
                """,

                colour=0xFFFFFF
                ),
                ephemeral=True
            )
