# Defines an asynchronous function `send_update` that takes a Discord channel, manga title, chapter number, link, and optional manga_id.
# Constructs an embedded message with the manga thumbnail, title, chapter number, and link.

import discord
import aiohttp

async def send_update(channel, title, chapter, link, manga_id=None):
    embed = discord.Embed(
        title="📖 New Chapter Released",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Manga Title", value=title, inline=False)
    embed.add_field(name="Chapter", value=chapter, inline=False)
    embed.add_field(name="Link", value=link, inline=False)
    
    # Fetch cover art if manga_id is provided
    if manga_id:
        try:
            async with aiohttp.ClientSession() as session:
                # Get manga info to find cover
                async with session.get(f"https://api.mangadex.org/manga/{manga_id}") as resp:
                    if resp.status == 200:
                        manga_data = await resp.json()
                        covers = manga_data.get("data", {}).get("relationships", [])
                        for cover_rel in covers:
                            if cover_rel.get("type") == "cover_art":
                                cover_filename = cover_rel.get("attributes", {}).get("fileName", "")
                                if cover_filename:
                                    cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_filename}"
                                    embed.set_thumbnail(url=cover_url)
                                    break
        except Exception as e:
            print(f"Failed to fetch cover art: {e}")
    
    await channel.send(embed=embed)