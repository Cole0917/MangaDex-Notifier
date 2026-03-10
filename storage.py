import json
import os

HISTORY_FILE = "history.json"

# Loads the history of notified manga chapters from a JSON file. If the file does not exist, it returns an empty dictionary.
def load_history():

    if not os.path.exists(HISTORY_FILE):
        return {}

    with open(HISTORY_FILE) as f:
        return json.load(f)

# Saves the history of notified manga chapters to a JSON file, formatting it with an indentation of 2 for readability.
def save_history(history):

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)