# MangaDex Updates Notifier Tool

A Discord bot to track MangaDex manga updates, support follow lists, channel notifications, and command helpers.

## Requirements


## Installation



## Usage

Run:
```bash
python main.py
```

### Slash commands
- `/help` – show all available commands
- `/following` – list your manga follows
- `/follow <manga_url>` – follow MangaDex manga (supports `/title/` and `/manga/` URL formats)
- `/setchannel <channel>` – configure update channel in Discord for the invoking user
- `/checkcurrentchapter <number>` - check for a current chapter of a followed manga
- `/remove <number>` - remove a manga from your followed list by its index in /following
- `/coinflip` – 50/50 Heads/Tails response


## Notes

- Make sure the bot has the `Send Messages` and `Embed Links` channel permissions.


