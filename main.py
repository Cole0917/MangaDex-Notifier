import time
import json
import mangadex_api
import notifier
import storage

# Loads the configuration from the JSON file, extracting the username, password, and check interval for the MangaDex notifier.
with open("config.json") as f:
    config = json.load(f)

username = config["username"]
password = config["password"]
interval = config["check_interval"]

print("Logging into MangaDex...")

# Logs in to the MangaDex API using the provided credentials and retrieves a session token for authenticated requests.
session = mangadex_api.login(username, password)

print("Fetching followed manga...")

# Retrieves the list of manga followed by the user, using the session token for authentication. It returns a list of manga with their IDs and titles.
manga_list = mangadex_api.get_followed_manga(session)

history = storage.load_history()

print(f"Tracking {len(manga_list)} manga")

# Enters an infinite loop to continuously check for new chapters of the followed manga. For each manga, it retrieves the latest chapter and compares it with the history. If a new chapter is found, it sends a desktop notification and updates the history. The loop sleeps for the specified interval before checking again.
while True:

    for manga in manga_list:

        manga_id = manga["id"]
        title = manga["title"]

        chapter = mangadex_api.get_latest_chapter(manga_id)

        if chapter is None:
            continue

        if manga_id not in history:
            history[manga_id] = chapter

        elif history[manga_id] != chapter:

            history[manga_id] = chapter

            notifier.send(title, chapter)

            print(f"New chapter: {title} {chapter}")

    storage.save_history(history)

    time.sleep(interval)