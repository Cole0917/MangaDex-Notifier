import asyncio
import aiohttp
import json
import mangadex_api
import notifier
import storage

# Checks for new chapters of followed manga in a loop, sending notifications when new chapters are found. It loads the history of notified chapters and saves it after each check to avoid duplicate notifications.
async def check_loop(session, token, interval):
    history = await storage.load_history()
    with open("config.json") as f:
        config = json.load(f)
    discord_token = config.get("discord_bot_token")
    discord_channel = config.get("discord_channel_id")

    if discord_token and discord_channel:
        notifier.setup_discord(discord_token, discord_channel)

    manga_list = await mangadex_api.get_followed_manga(session, token)
    print(f"Tracking {len(manga_list)} manga")

    while True:
        tasks = []
        for manga in manga_list:
            tasks.append(check_manga(session, manga, history))
        await asyncio.gather(*tasks)
        await storage.save_history(history)
        await asyncio.sleep(interval)

# Checks for new chapters of a specific manga and sends notifications if a new chapter is found. It updates the history to keep track of the latest chapter notified.
async def check_manga(session, manga, history):
    manga_id = manga["id"]
    title = manga["title"]
    chapter = await mangadex_api.get_latest_chapter(session, manga_id)
    if not chapter:
        return

    if manga_id not in history or history[manga_id] != chapter:
        history[manga_id] = chapter
        notifier.send_desktop(title, chapter)
        await notifier.send_discord(title, chapter)
        print(f"New chapter: {title} {chapter}")

# Main entry point of the program, which loads the configuration, logs into MangaDex, and starts the check loop to monitor for new manga chapters.
async def main():
    with open("config.json") as f:
        config = json.load(f)

    interval = config.get("check_interval", 600)
    username = config["username"]
    password = config["password"]

    async with aiohttp.ClientSession() as session:
        token = await mangadex_api.login(session, username, password)
        await check_loop(session, token, interval)

if __name__ == "__main__":
    asyncio.run(main())