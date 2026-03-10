import json
import asyncio

HISTORY_FILE = "history.json"

# Loads the history of manga chapters from a JSON file, returning an empty dictionary if the file does not exist.
async def load_history():
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Saves the history of manga chapters to a JSON file, allowing the program to track which chapters have already been notified about.
async def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)