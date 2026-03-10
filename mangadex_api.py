import aiohttp
import asyncio

BASE_URL = "https://api.mangadex.org"

# Fetches an authentication token for the user using their username and password, returning the session token if successful.
async def login(session, username, password):
    url = f"{BASE_URL}/auth/login"
    async with session.post(url, json={"username": username, "password": password}) as resp:
        data = await resp.json()
        return data["token"]["session"]

# Fetches the list of manga followed by the user, returning a list of dictionaries containing manga IDs and titles.
async def get_followed_manga(session, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/user/follows/manga"
    async with session.get(url, headers=headers) as resp:
        data = await resp.json()
        manga = []
        for item in data["data"]:
            title = list(item["attributes"]["title"].values())[0]
            manga.append({"id": item["id"], "title": title})
        return manga

# Fetches the latest chapter number for a given manga ID, returning None if no chapters are found.
async def get_latest_chapter(session, manga_id):
    url = f"{BASE_URL}/chapter"
    params = {
        "manga": manga_id,
        "limit": 1,
        "translatedLanguage[]": "en",
        "order[chapter]": "desc"
    }
    async with session.get(url, params=params) as resp:
        data = await resp.json()
        if not data["data"]:
            return None
        return data["data"][0]["attributes"]["chapter"]