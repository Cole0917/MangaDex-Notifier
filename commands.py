import discord
from discord.ext import commands
import aiohttp
import json
import os
import random

class MangaListView(discord.ui.View):
    def __init__(self, user_id, manga_items, page_size, total_pages):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.manga_items = manga_items
        self.page_size = page_size
        self.total_pages = total_pages
        self.current_page = 1

    async def update_embed(self, interaction):
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        page_items = self.manga_items[start:end]

        embed = discord.Embed(title=f"{interaction.user.name}'s Followed Manga (page {self.current_page}/{self.total_pages})", color=discord.Color.green())
        for idx, (manga_id, manga_data) in enumerate(page_items, start + 1):
            embed.add_field(name=f"{idx}. {manga_data['title']}", value=manga_data["url"], inline=False)

        if self.total_pages > 1:
            embed.set_footer(text=f"Total items: {len(self.manga_items)}")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages:
            self.current_page += 1
            await self.update_embed(interaction)

class MangaDexCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.followed_file = "followed_manga.json"
        self.channels_file = "user_channels.json"
        self.load_followed()
        self.load_channels()

    def load_followed(self):
        if os.path.exists(self.followed_file):
            with open(self.followed_file, "r") as f:
                self.followed_manga = json.load(f)
        else:
            self.followed_manga = {}

    def save_followed(self):
        with open(self.followed_file, "w") as f:
            json.dump(self.followed_manga, f, indent=2)

    def load_channels(self):
        if os.path.exists(self.channels_file):
            with open(self.channels_file, "r") as f:
                self.user_channels = json.load(f)
        else:
            self.user_channels = {}

    def save_channels(self):
        with open(self.channels_file, "w") as f:
            json.dump(self.user_channels, f, indent=2)

    # Define slash commands for help, following, follow, and setchannel
    @discord.app_commands.command(name="help", description="Display list of all commands")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="MangaDex Notifier Commands", color=discord.Color.blue())
        embed.add_field(name="/help", value="Show all available commands", inline=False)
        embed.add_field(name="/following", value="Display your followed manga list", inline=False)
        embed.add_field(name="/follow <manga_url>", value="Add a manga to your followed list with a valid MangaDex URL", inline=False)
        embed.add_field(name="/setchannel <channel>", value="Set the channel for manga update notifications", inline=False)
        embed.add_field(name="/remove <number>", value="Remove a manga from your followed list by its number in /following", inline=False)
        embed.add_field(name="/checkcurrentchapter <number>", value="Check for current chapter of a followed manga. Index value is the number next to the manga on your /following list", inline=False)
        embed.add_field(name="/coinflip", value="Flip a coin - Heads or Tails", inline=False)
        await interaction.response.send_message(embed=embed)

    # Command to display followed manga for the user
    @discord.app_commands.command(name="following", description="Display followed manga")
    async def following_command(self, interaction: discord.Interaction, page: int = 1):
        user_id = str(interaction.user.id)
        if user_id not in self.followed_manga or not self.followed_manga[user_id]:
            await interaction.response.send_message("You are not following any manga yet!")
            return

        manga_items = list(self.followed_manga[user_id].items())
        page_size = 10
        total = len(manga_items)
        total_pages = (total + page_size - 1) // page_size

        if page < 1 or page > total_pages:
            await interaction.response.send_message(f"Invalid page number. Choose between 1 and {total_pages}.")
            return

        start = (page - 1) * page_size
        end = start + page_size
        page_items = manga_items[start:end]

        embed = discord.Embed(title=f"{interaction.user.name}'s Followed Manga (page {page}/{total_pages})", color=discord.Color.green())
        for idx, (manga_id, manga_data) in enumerate(page_items, start + 1):
            embed.add_field(name=f"{idx}. {manga_data['title']}", value=manga_data["url"], inline=False)

        if total_pages > 1:
            embed.set_footer(text=f"Use /following <page> to see other pages. Total items: {total}")

        await interaction.response.send_message(embed=embed)

    # Command to follow a manga by URL
    @discord.app_commands.command(name="follow", description="Follow a manga")
    async def follow_command(self, interaction: discord.Interaction, manga_url: str):
        try:
            # Extract manga ID from URL - support both /title/ and /manga/ formats
            if "/title/" in manga_url:
                manga_id = manga_url.split("/title/")[1].split("/")[0]
            elif "/manga/" in manga_url:
                manga_id = manga_url.split("/manga/")[1].split("/")[0]
            else:
                await interaction.response.send_message("Invalid manga URL! Use a MangaDex URL like: https://mangadex.org/title/UUID/manga-name")
                return
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.mangadex.org/manga/{manga_id}") as resp:
                    if resp.status != 200:
                        await interaction.response.send_message("Invalid manga URL or ID!")
                        return
                    data = await resp.json()
                    
                    # Try to get English title, fallback to any available title
                    titles = data["data"]["attributes"]["title"]
                    if isinstance(titles, dict):
                        manga_title = titles.get("en") or next(iter(titles.values())) if titles else "Unknown Manga"
                    else:
                        manga_title = titles or "Unknown Manga"

            user_id = str(interaction.user.id)
            if user_id not in self.followed_manga:
                self.followed_manga[user_id] = {}

            self.followed_manga[user_id][manga_id] = {"title": manga_title, "url": manga_url}
            self.save_followed()

            await interaction.response.send_message(f"✅ Added **{manga_title}** to your followed list!")
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")

    # Command to set the notification channel for the user (admin-only)
    @discord.app_commands.command(name="setchannel", description="Set the channel for manga update notifications")
    async def setchannel_command(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
                return

            user_id = str(interaction.user.id)
            self.user_channels[user_id] = str(channel.id)
            self.save_channels()
            await interaction.response.send_message(f"✅ Notification channel set to {channel.mention}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")

    # Command to flip a coin with 50/50 chance
    @discord.app_commands.command(name="coinflip", description="Flip a coin - Heads or Tails")
    async def coinflip_command(self, interaction: discord.Interaction):
        result = "Heads!" if random.choice([True, False]) else "Tails!"
        await interaction.response.send_message(result)

    # Command to remove a manga from followed list by number
    @discord.app_commands.command(name="remove", description="Remove manga from your followed list by number")
    async def remove_command(self, interaction: discord.Interaction, index: int):
        try:
            user_id = str(interaction.user.id)
            if user_id not in self.followed_manga or not self.followed_manga[user_id]:
                await interaction.response.send_message("Your followed list is empty.")
                return

            if index < 1 or index > len(self.followed_manga[user_id]):
                await interaction.response.send_message("Invalid number. Use /following to see the list and indexing.")
                return

            manga_items = list(self.followed_manga[user_id].items())
            manga_id, manga_data = manga_items[index - 1]
            del self.followed_manga[user_id][manga_id]
            self.save_followed()
            await interaction.response.send_message(f"✅ Removed **{manga_data['title']}** from your followed list.")
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")

    # Command to check latest chapter of a followed manga by index
    @discord.app_commands.command(name="checkcurrentchapter", description="Check the latest chapter of a manga in your followed list")
    async def checkcurrentchapter_command(self, interaction: discord.Interaction, index: int):
        try:
            user_id = str(interaction.user.id)
            if user_id not in self.followed_manga or not self.followed_manga[user_id]:
                await interaction.response.send_message("Your followed list is empty.")
                return

            if index < 1 or index > len(self.followed_manga[user_id]):
                await interaction.response.send_message("Manga not available in your list!")
                return

            manga_items = list(self.followed_manga[user_id].items())
            manga_id, manga_data = manga_items[index - 1]

            # Import mangadex_api to get latest chapter
            import mangadex_api
            latest = await mangadex_api.get_latest_chapter(manga_id)
            if not latest:
                await interaction.response.send_message("Unable to fetch latest chapter information.")
                return

            embed = discord.Embed(title=f"Latest Chapter for {manga_data['title']}", color=discord.Color.blue())
            embed.add_field(name="Chapter", value=latest["chapter"], inline=False)
            embed.add_field(name="Link", value=f"https://mangadex.org/chapter/{latest['id']}", inline=False)

            # Fetch cover art via the cover endpoint
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.mangadex.org/manga/{manga_id}") as resp:
                        if resp.status == 200:
                            manga_data_resp = await resp.json()
                            relationships = manga_data_resp.get("data", {}).get("relationships", [])
                            cover_id = None
                            for rel in relationships:
                                if rel.get("type") == "cover_art":
                                    cover_id = rel.get("id")
                                    break

                            if cover_id:
                                async with session.get(f"https://api.mangadex.org/cover/{cover_id}") as cover_resp:
                                    if cover_resp.status == 200:
                                        cover_data = await cover_resp.json()
                                        filename = cover_data.get("data", {}).get("attributes", {}).get("fileName")
                                        if filename:
                                            cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{filename}"
                                            embed.set_thumbnail(url=cover_url)
            except Exception as e:
                print(f"Failed to fetch cover art: {e}")

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")

# This function will be called when the cog is loaded, and it adds the cog to the bot
async def setup(bot):
    await bot.add_cog(MangaDexCommands(bot))