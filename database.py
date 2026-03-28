from motor.motor_asyncio import AsyncIOMotorClient
from config import config 

client = AsyncIOMotorClient(config["mongo_uri"])
db = client["mangadex_notifier"]

users = db.users

async def get_user(user_id):
    user = await users.find_one({"user_id": str(user_id)})
    if not user:
        user = {"user_id": str(user_id), "channel_id": None, "manga": []}
        await users.insert_one(user)
    return user

# Update the channel ID for a user
async def set_channel(user_id, channel_id):
    await users.update_one(
        {"user_id": str(user_id)},
        {"$set": {"channel_id": str(channel_id)}},
        upsert=True
    )

# Add a manga to the user's manga list
async def add_manga(user_id, manga):
    await users.update_one(
        {"user_id": str(user_id)},
        {"$push": {"manga": manga}},
        upsert=True
    )

# Remove a manga from the user's manga list
async def remove_manga(user_id, manga_id):
    await users.update_one(
        {"user_id": str(user_id)},
        {"$pull": {"manga": {"id": manga_id}}}
    )

# Update latest chapter for a user's manga entry
async def update_manga_chapter(user_id, manga_id, last_chapter):
    await users.update_one(
        {"user_id": str(user_id), "manga.id": manga_id},
        {"$set": {"manga.$.last_chapter": last_chapter}}
    )

# Get all users
async def get_all_users():
    return await users.find({}).to_list(length=None)