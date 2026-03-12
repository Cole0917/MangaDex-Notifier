# Defines an asynchronous function `send_update` that takes a Discord channel, manga title, chapter number, and link as parameters. It constructs a message string containing the manga title, chapter number, and link, formatted with Markdown for better readability. The function then sends this message to the specified Discord channel using the `send` method.

async def send_update(channel, title, chapter, link):

    msg = f"""
📖 **New Chapter Released**

**{title}**
Chapter {chapter}

{link}
"""

    await channel.send(msg)