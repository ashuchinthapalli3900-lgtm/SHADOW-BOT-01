import discord
import instaloader
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 145962966558
USERNAME = 'dragon__up'

L = instaloader.Instaloader()
last_shortcode = None

def check_instagram():
    global last_shortcode
    try:
        profile = instaloader.Profile.from_username(L.context, USERNAME)
        posts = list(profile.get_posts())
        if posts:
            latest = posts[0]
            if latest.shortcode != last_shortcode:
                last_shortcode = latest.shortcode
                return f"https://www.instagram.com/p/{latest.shortcode}/"
    except Exception as e:
        print(f"Error checking Instagram: {e}")
    return None

bot = discord.Client(intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Set initial last_shortcode without sending
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, check_instagram)
    # Start the checking loop
    asyncio.create_task(check_loop())

async def check_loop():
    while True:
        loop = asyncio.get_event_loop()
        link = await loop.run_in_executor(None, check_instagram)
        if link:
            channel = bot.get_channel(CHANNEL_ID)
            await channel.send(link)
        await asyncio.sleep(1200)  # 20 minutes

bot.run(TOKEN)