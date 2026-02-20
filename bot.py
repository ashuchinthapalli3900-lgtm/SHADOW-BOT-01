import os
import json
import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
import instaloader
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Instaloader setup
L = instaloader.Instaloader()
USERNAME = 'dragon___up'
LAST_POST_FILE = 'last_post.txt'

# Config file for channel ID
CONFIG_FILE = 'config.json'

def get_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_last_shortcode():
    try:
        with open(LAST_POST_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_shortcode(shortcode):
    with open(LAST_POST_FILE, 'w') as f:
        f.write(shortcode)

def check_instagram():
    try:
        profile = instaloader.Profile.from_username(L.context, USERNAME)
        posts = list(profile.get_posts())
        if posts:
            latest = posts[0]
            return latest.shortcode
    except Exception as e:
        print(f"Error checking Instagram: {e}")
    return None

class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync commands
        await self.tree.sync()
        # Start the background task
        self.check_instagram_task.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

@tasks.loop(minutes=20)
async def check_instagram_task():
    latest_shortcode = check_instagram()
    if latest_shortcode:
        last_shortcode = get_last_shortcode()
        if latest_shortcode != last_shortcode:
            link = f"https://www.instagram.com/p/{latest_shortcode}/"
            config = get_config()
            channel_id = config.get('notify_channel')
            if channel_id:
                channel = bot.get_channel(int(channel_id))
                if channel:
                    await channel.send(f"New post from {USERNAME}: {link}")
                    save_last_shortcode(latest_shortcode)
                    print(f"Sent notification to channel {channel_id}")
                else:
                    print(f"Channel {channel_id} not found")
            else:
                print("No notify channel set")
        else:
            print("No new post")
    else:
        print("No posts found")

bot = MyBot(intents=discord.Intents.default())

@bot.tree.command(name="notifychannel", description="Set the channel for Instagram notifications (Admin only)")
@app_commands.describe(channel_id="The ID of the Discord channel")
async def notifychannel(interaction: discord.Interaction, channel_id: str):
    # Check if user is admin
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return

    try:
        # Validate channel ID
        channel = bot.get_channel(int(channel_id))
        if not channel:
            await interaction.response.send_message("Invalid channel ID.", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("Invalid channel ID format.", ephemeral=True)
        return

    config = get_config()
    config['notify_channel'] = channel_id
    save_config(config)
    await interaction.response.send_message(f"Notification channel set to <#{channel_id}>", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)