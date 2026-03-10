import requests

# Mangadex API communication handling for basic operations: login, get followed manga, and get latest chapter.

BASE_URL = "https://api.mangadex.org"


# Logs in to the Mangadex API using the provided username and password, returning a session token for authenticated requests.
def login(username, password):

    url = f"{BASE_URL}/auth/login"

    payload = {
        "username": username,
        "password": password
    }

    r = requests.post(url, json=payload)
    data = r.json()

    return data["token"]["session"]

# Retrieves the list of manga followed by the user, using the session token for authentication. It returns a list of manga with their IDs and titles.
def get_followed_manga(session_token):

    headers = {
        "Authorization": f"Bearer {session_token}"
    }

    url = f"{BASE_URL}/user/follows/manga"

    r = requests.get(url, headers=headers)
    data = r.json()

    manga = []

    for item in data["data"]:

        title = list(item["attributes"]["title"].values())[0]

        manga.append({
            "id": item["id"],
            "title": title
        })

    return manga

# Retrieves the latest chapter number for a given manga ID by querying the Mangadex API. It returns the chapter number as a string, or None if no chapters are found.
def get_latest_chapter(manga_id):

    url = f"{BASE_URL}/chapter"

    params = {
        "manga": manga_id,
        "limit": 1,
        "translatedLanguage[]": "en",
        "order[chapter]": "desc"
    }

    r = requests.get(url, params=params)
    data = r.json()

    if not data["data"]:
        return None

    chapter = data["data"][0]["attributes"]["chapter"]

    return chapter