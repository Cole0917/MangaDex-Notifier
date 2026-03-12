from motor.motor_asyncio import AsyncIOMotorClient
from config import config 

client = AsyncIOMotorClient(config["mongo_uri"])
db = client["mangadex_notifier"]

guilds = db.guilds


async def get_guild(guild_id):
    guild = await guilds.find_one({"guild_id": str(guild_id)})
    if not guild:
        guild = {"guild_id": str(guild_id), "channel_id": None, "manga": []}
        await guilds.insert_one(guild)
    return guild

# Update the channel ID for a guild
async def set_channel(guild_id, channel_id):
    await guilds.update_one(
        {"guild_id": str(guild_id)},
        {"$set": {"channel_id": str(channel_id)}},
        upsert=True
    )

# Add a manga to the guild's manga list
async def add_manga(guild_id, manga):
    await guilds.update_one(
        {"guild_id": str(guild_id)},
        {"$push": {"manga": manga}}
    )

# Remove a manga from the guild's manga list
async def remove_manga(guild_id, manga_id):
    await guilds.update_one(
        {"guild_id": str(guild_id)},
        {"$pull": {"manga": {"id": manga_id}}}
    )

# Get all guilds
async def get_all_guilds():
    return await guilds.find({}).to_list(length=None)