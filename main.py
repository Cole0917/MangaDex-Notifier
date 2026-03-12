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
        guild_list = await database.get_all_guilds()  # get all guilds as a list
        for guild in guild_list:
            channel_id = guild.get("channel_id")
            if not channel_id:
                continue

            channel = bot.get_channel(int(channel_id))

            for manga in guild["manga"]:
                latest = await mangadex_api.get_latest_chapter(manga["id"])
                if not latest:
                    continue
                if latest["chapter"] != manga["last_chapter"]:
                    link = f"https://mangadex.org/chapter/{latest['id']}"
                    await notifier.send_update(
                        channel,
                        manga["title"],
                        latest["chapter"],
                        link
                    )

        await asyncio.sleep(CHECK_INTERVAL)

# Command to set the channel for updates
@bot.event
async def on_ready():
    print("Bot online:", bot.user)
    asyncio.create_task(check_updates())

# Run the bot
bot.run(config["discord_token"])