# 🏁 MX Bikes Hotlap Bot — Setup Guide

## What This Bot Does
- `/hotlap` — Submit a hotlap with track, bike, and time (shows a clean embed)
- `/leaderboard` — View top times for any track (filterable by 250cc/450cc)
- `/pb` — View your personal bests across all tracks
- `/tracks` — List all tracks with recorded times
- Auto-detects personal bests and highlights them with 🔥

---

## Step 1: Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** → Name it something like `MX Hotlap Bot`
3. Go to the **"Bot"** tab on the left
4. Click **"Reset Token"** → Copy the token (you'll need this!)
5. Scroll down and enable **"Message Content Intent"**

## Step 2: Invite the Bot to Your Server

1. Go to the **"OAuth2"** tab → **"URL Generator"**
2. Under **Scopes**, check: `bot` and `applications.commands`
3. Under **Bot Permissions**, check:
   - Send Messages
   - Embed Links
   - Use Slash Commands
4. Copy the generated URL and open it in your browser
5. Select **WLG GANG** and authorize

## Step 3: Install Python & Run the Bot

### Install Python
- Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
- During install, check **"Add Python to PATH"**

### Set Up the Bot
1. Download the bot files (`bot.py` and `requirements.txt`)
2. Open a terminal/command prompt in the bot folder
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Open `bot.py` and replace `YOUR_BOT_TOKEN_HERE` with your bot token:
   ```python
   BOT_TOKEN = "paste-your-token-here"
   ```
5. Run the bot:
   ```
   python bot.py
   ```
6. You should see:
   ```
   ✅ MX Hotlap Bot is online!
   ✅ Synced 4 slash commands
   ```

---

## Step 4: Hosting (Keeping the Bot Online 24/7)

Since you need guidance on hosting, here are your best options:

### Option A: Your Own PC (Free, Easiest)
- Just keep `python bot.py` running in a terminal
- **Downside:** Bot goes offline when your PC is off

### Option B: Railway (Free Tier Available)
1. Create an account at [railway.app](https://railway.app)
2. Create a new project → Deploy from GitHub or upload files
3. Add an environment variable: `BOT_TOKEN` = your token
4. The bot runs 24/7 on their servers
5. **Free tier gives you 500 hours/month** (enough for most use)

### Option C: Oracle Cloud Free Tier (Free Forever)
1. Sign up at [Oracle Cloud](https://cloud.oracle.com) (free tier)
2. Create a free compute instance (VM)
3. SSH in, upload the bot files, install Python
4. Run with: `nohup python bot.py &`
5. **Truly free and runs 24/7**

### Option D: A Raspberry Pi (One-Time Cost ~$35)
- Plug it in at home and let it run forever
- Very low power usage

---

## Using the Bot

### Submit a hotlap:
```
/hotlap track:Wolf Creek bike:KTM 250 time:1:56.41
```

### View leaderboard:
```
/leaderboard track:Wolf Creek
/leaderboard track:Wolf Creek bike_class:250cc
```

### View your personal bests:
```
/pb
```

### List all tracks:
```
/tracks
```

---

## Pinned Message Template

Pin this in #mx-bikes-hotlaps for anyone who wants to post manually too:

```
🏁 **Hotlap Submission**
📍 Track: 
🏍️ Bike: 
⏱️ Time: 
📅 Date: 
```

---

## Need Help?
If you run into issues, the most common fixes are:
- Make sure your bot token is correct
- Make sure you enabled "Message Content Intent" in the Developer Portal
- Make sure Python 3.10+ is installed
- Try `pip install --upgrade discord.py` if you get import errors
