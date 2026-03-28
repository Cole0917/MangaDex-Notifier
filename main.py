import discord
import asyncio
import json

import database
import mangadex_api
import notifier

from discord.ext import commands
from config import config

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

CHECK_INTERVAL = config["check_interval"]

# This function will run in the background and check for manga updates every CHECK_INTERVAL seconds
async def check_updates():
    while not bot.is_closed():
        users_list = await database.get_all_users()  # get all users as a list
        for user in users_list:
            channel_id = user.get("channel_id")
            if not channel_id:
                continue

            channel = bot.get_channel(int(channel_id))
            if channel is None:
                continue

            for manga in user.get("manga", []):
                latest = await mangadex_api.get_latest_chapter(manga["id"])
                if not latest:
                    continue

                if manga.get("last_chapter") is None or latest["chapter"] != manga.get("last_chapter"):
                    link = f"https://mangadex.org/chapter/{latest['id']}"
                    await notifier.send_update(
                        channel,
                        manga["title"],
                        latest["chapter"],
                        link,
                        manga["id"]
                    )
                    # Update last known chapter
                    await database.update_manga_chapter(user.get("user_id"), manga["id"], latest["chapter"])

        await asyncio.sleep(CHECK_INTERVAL)

# When the bot is ready, it will print a message and start the background task to check for updates
@bot.event
async def on_ready():
    print("Bot online:", bot.user)
    
    # Load slash command cog
    try:
        await bot.load_extension("commands")
        print("Loaded commands cog")
    except Exception as e:
        print(f"Failed to load commands cog: {e}")
    
    # Sync application commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} application commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Set bot status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))
    
    asyncio.create_task(check_updates())

# Run the bot
bot.run(config["discord_token"])
