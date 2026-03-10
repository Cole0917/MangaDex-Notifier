from plyer import notification
import discord
import asyncio

discord_client = None
discord_channel_id = None

# Sends a desktop notification when a new manga chapter is released, using the provided title and chapter number. The notification will display for 10 seconds.
def send_desktop(title, chapter):
    notification.notify(
        title="New Manga Chapter!",
        message=f"{title} - Chapter {chapter}",
        timeout=10
    )

# Sends a notification to the configured Discord channel when a new manga chapter is released, using the provided title and chapter number. If the Discord client is not set up, it simply returns without sending a notification.
async def send_discord(title, chapter):
    if discord_client is None:
        return
    channel = discord_client.get_channel(discord_channel_id)
    if channel:
        await channel.send(f"**{title}** - Chapter {chapter} released!")

# Sets up the Discord bot with the provided token and channel ID, allowing it to send notifications to the specified channel when new manga chapters are released.
def setup_discord(token, channel_id):
    global discord_client, discord_channel_id
    discord_client = discord.Client(intents=discord.Intents.default())
    discord_channel_id = int(channel_id)

    @discord_client.event
    async def on_ready():
        print(f"Discord bot logged in as {discord_client.user}")

    asyncio.create_task(discord_client.start(token))