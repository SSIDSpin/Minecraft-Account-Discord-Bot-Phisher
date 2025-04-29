import discord
import json
from discord import ui, TextInput  
from views.button_one import ButtonViewOne

class MyModalThree(ui.Modal, title="Verification"):
    box_one = ui.TextInput(label="Title",placeholder="Your Custom Title", required=True)
    box_two = ui.TextInput(label="Verify Message",style=discord.TextStyle.paragraph,placeholder="Your Custom Message", required=True)
    box_three = ui.TextInput(label="Colour Hex Code",placeholder="e.g #FF5733", required=True)
    box_four = ui.TextInput(label="Webhook",placeholder="https://discord.com/api/webhooks/" ,required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # Retrieve values from the text inputs
        title = self.box_one.value
        description = self.box_two.value
        colour_hex = self.box_three.value
        webhook = self.box_four.value
        with open("data.json", "w") as f:
            json.dump({"webhook": webhook}, f, indent=4)

        try:
            # Convert the hex code to a Discord Colour
            colour = discord.Colour(int(colour_hex.lstrip("#"), 16))

            # Create the embed
            embed = discord.Embed(
                title=title,
                description=description,
                colour=colour  # Use the parsed color here
            )

            # Send the embed with the button view
            await interaction.response.send_message(f"The webhook URL has been set to: {webhook}", ephemeral=True)
            await interaction.channel.send(embed=embed, view=ButtonViewOne())
            

        except ValueError:
            await interaction.response.send_message(
                f"Invalid colour hex code: {colour_hex}. Please use a valid hex code (e.g., #FF5733).",
                ephemeral=True
            )
