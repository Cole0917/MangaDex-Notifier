import aiohttp

BASE_URL = "https://api.mangadex.org"

# Gets manga details such as the title for a given manga ID by sending a GET request to the MangaDex API. It retrieves the manga's title in English if available; otherwise, it defaults to "Unknown". The function returns the manga title as a string.
async def get_manga(manga_id):

    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/manga/{manga_id}"

        async with session.get(url) as resp:
            data = await resp.json()

            title = data["data"]["attributes"]["title"].get("en", "Unknown")

            return title

# Fetches the latest chapter information for a given manga ID from the MangaDex API. It sends a GET request to the manga feed endpoint, requesting only the most recent chapter in English. If a chapter is found, it returns a dictionary containing the chapter's ID and chapter number; otherwise, it returns None.
async def get_latest_chapter(manga_id):

    async with aiohttp.ClientSession() as session:

        url = f"{BASE_URL}/manga/{manga_id}/feed"

        params = {
            "limit": 1,
            "translatedLanguage[]": "en",
            "order[publishAt]": "desc"
        }

        async with session.get(url, params=params) as resp:
            data = await resp.json()

            if not data["data"]:
                return None

            chapter = data["data"][0]

            return {
                "id": chapter["id"],
                "chapter": chapter["attributes"]["chapter"]
            }